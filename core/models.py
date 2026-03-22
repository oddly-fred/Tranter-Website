from django.db import models
from django.utils import timezone
from django.utils.text import slugify

# Create your models here.
class Service(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    is_available_in_nigeria = models.BooleanField(default=True)
    is_available_global = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    

    # core/models.py (events section) — or create events/models.py
# These models power the full event system.

class EventCategory(models.Model):
    """Event category — Tech Workshop, Webinar, Conference, etc."""
    name   = models.CharField(max_length=80)
    slug   = models.SlugField(unique=True)
    icon   = models.CharField(max_length=10, default='📅', help_text='Emoji icon')
    color  = models.CharField(
        max_length=10,
        choices=[('green', 'Green'), ('red', 'Red')],
        default='green'
    )
    order  = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Event Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Event(models.Model):
    """Main event model — handles all event types."""

    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('live',     'Live Now'),
        ('past',     'Past'),
    ]
    ACCESS_CHOICES = [
        ('all',    'All Users'),
        ('ng',     'Nigeria Only'),
        ('global', 'Global Only'),
    ]
    TYPE_CHOICES = [
        ('workshop',   'Tech Workshop'),
        ('training',   'Corporate Training'),
        ('webinar',    'Webinar'),
        ('launch',     'Product Launch'),
        ('internal',   'Internal Staff Event'),
        ('conference', 'Conference'),
    ]

    # ── Core fields
    title        = models.CharField(max_length=200)
    slug         = models.SlugField(unique=True, blank=True)
    category     = models.ForeignKey(
        EventCategory, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='events'
    )
    event_type   = models.CharField(max_length=20, choices=TYPE_CHOICES, default='webinar')
    tagline      = models.CharField(max_length=200, blank=True)
    description  = models.TextField()
    status       = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')
    access       = models.CharField(max_length=10, choices=ACCESS_CHOICES, default='all',
                                    help_text='Who sees this event based on geo')

    # ── Date & location
    date         = models.DateTimeField()
    end_date     = models.DateTimeField(blank=True, null=True)
    location     = models.CharField(max_length=200, blank=True,
                                    help_text='Physical address or "Online"')
    is_online    = models.BooleanField(default=False)
    timezone_label = models.CharField(max_length=40, default='WAT',
                                      help_text='e.g. WAT, GMT, EST')

    # ── Media
    cover_image  = models.ImageField(upload_to='events/covers/', blank=True, null=True)
    banner_image = models.ImageField(upload_to='events/banners/', blank=True, null=True,
                                     help_text='Wide banner for hero section')
    video_recap  = models.URLField(blank=True, help_text='YouTube embed URL for past event recap')

    # ── Registration & links
    registration_url = models.URLField(blank=True, help_text='External Zoom/Eventbrite link')
    is_free      = models.BooleanField(default=True)
    price_ng     = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                       help_text='Price in NGN (₦)')
    price_global = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                       help_text='Price in USD ($)')

    # ── Event stats (editable after event)
    attendees_count = models.PositiveIntegerField(default=0)
    partners_count  = models.PositiveIntegerField(default=0)
    speakers_count  = models.PositiveIntegerField(default=0)
    sessions_count  = models.PositiveIntegerField(default=0)

    # ── Flags
    is_featured  = models.BooleanField(default=False,
                                       help_text='Show in featured hero section')
    is_active    = models.BooleanField(default=True)

    # ── SEO
    meta_title       = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=300, blank=True)

    # ── Timestamps
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.title} ({self.get_status_display()})'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        # Auto-update status based on date
        now = timezone.now()
        if self.status != 'live':
            if self.date > now:
                self.status = 'upcoming'
            else:
                self.status = 'past'
        super().save(*args, **kwargs)

    @property
    def is_upcoming(self):
        return self.date > timezone.now()

    @property
    def days_until(self):
        if self.is_upcoming:
            return (self.date - timezone.now()).days
        return 0

    @property
    def countdown_data(self):
        """Returns dict for JS countdown timer."""
        if not self.is_upcoming:
            return None
        now   = timezone.now()
        delta = self.date - now
        total = int(delta.total_seconds())
        return {
            'target_iso': self.date.isoformat(),
            'days':    delta.days,
            'hours':   (total % 86400) // 3600,
            'minutes': (total % 3600) // 60,
            'seconds': total % 60,
        }

    def get_price(self, is_nigeria=True):
        if self.is_free:
            return 'Free'
        if is_nigeria and self.price_ng:
            return f'₦{self.price_ng:,.0f}'
        if not is_nigeria and self.price_global:
            return f'${self.price_global:,.0f}'
        return 'Free'


class EventGalleryImage(models.Model):
    """Photo gallery for each event — supports masonry layout."""
    event   = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='gallery')
    image   = models.ImageField(upload_to='events/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    # Size hint for masonry layout
    size    = models.CharField(
        max_length=10,
        choices=[('small','Small'), ('medium','Medium'), ('large','Large')],
        default='medium'
    )
    order   = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.event.title} — image {self.order}'


class EventSpeaker(models.Model):
    """Speakers or hosts for an event."""
    event   = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='speakers')
    name    = models.CharField(max_length=120)
    role    = models.CharField(max_length=120, help_text='e.g. CEO, Tranter IT')
    photo   = models.ImageField(upload_to='events/speakers/', blank=True, null=True)
    bio     = models.TextField(blank=True, max_length=300)
    linkedin = models.URLField(blank=True)
    order   = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.name} @ {self.event.title}'


class EventTestimonial(models.Model):
    """Attendee quotes shown in the testimonials carousel."""
    event       = models.ForeignKey(
        Event, on_delete=models.CASCADE,
        related_name='testimonials', null=True, blank=True,
        help_text='Leave blank to show on all events page'
    )
    name        = models.CharField(max_length=120)
    role        = models.CharField(max_length=150, help_text='e.g. CTO, Zenith Bank')
    quote       = models.TextField(max_length=400)
    photo       = models.ImageField(upload_to='events/testimonials/', blank=True, null=True)
    rating      = models.PositiveIntegerField(default=5, help_text='1–5 stars')
    is_featured = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.quote[:60]}'

    @property
    def stars(self):
        return range(self.rating)

    @property
    def empty_stars(self):
        return range(5 - self.rating)
    





    # ── 1. ADD TO core/models.py ─────────────────────────────────────────────
 

 
 
class InsightCategory(models.Model):
    name  = models.CharField(max_length=80)
    slug  = models.SlugField(unique=True)
    icon  = models.CharField(max_length=10, default='📄')
    color = models.CharField(max_length=10,
                choices=[('green','Green'),('red','Red')], default='green')
    order = models.PositiveIntegerField(default=0)
 
    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Insight Categories'
 
    def __str__(self): return self.name
 
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name)
        super().save(*args, **kwargs)
 
 
class InsightTag(models.Model):
    name = models.CharField(max_length=60)
    slug = models.SlugField(unique=True)
 
    def __str__(self): return self.name
 
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name)
        super().save(*args, **kwargs)
 
 
class Insight(models.Model):
    TYPE_CHOICES = [
        ('article', 'Article'),
        ('report',  'Report (PDF)'),
        ('video',   'Video'),
        ('dashboard','KPI Dashboard'),
        ('sponsored','Sponsored / Premium'),
    ]
    AUDIENCE = [
        ('all',    'All'),
        ('ng',     'Nigeria Only'),
        ('global', 'Global Only'),
    ]
 
    title        = models.CharField(max_length=220)
    slug         = models.SlugField(unique=True, blank=True)
    category     = models.ForeignKey(InsightCategory, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='insights')
    tags         = models.ManyToManyField(InsightTag, blank=True)
    insight_type = models.CharField(max_length=12, choices=TYPE_CHOICES, default='article')
    audience     = models.CharField(max_length=8, choices=AUDIENCE, default='all')
 
    # Content
    excerpt      = models.TextField(max_length=320)
    body         = models.TextField(blank=True)
    cover_image  = models.ImageField(upload_to='insights/covers/', blank=True, null=True)
    video_url    = models.URLField(blank=True, help_text='YouTube embed URL')
 
    # Attachments
    pdf_file     = models.FileField(upload_to='insights/pdfs/', blank=True, null=True)
    pdf_label    = models.CharField(max_length=120, blank=True,
                                    default='Download Report')
 
    # Author
    author_name  = models.CharField(max_length=120, blank=True)
    author_role  = models.CharField(max_length=120, blank=True)
    author_photo = models.ImageField(upload_to='insights/authors/', blank=True, null=True)
 
    # Flags
    is_featured  = models.BooleanField(default=False)
    is_sponsored = models.BooleanField(default=False)
    is_premium   = models.BooleanField(default=False)
    is_archived  = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
 
    # Stats
    read_time    = models.PositiveIntegerField(default=5, help_text='Minutes')
    views        = models.PositiveIntegerField(default=0)
    likes        = models.PositiveIntegerField(default=0)
 
    # SEO
    meta_title       = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=320, blank=True)
 
    published_at = models.DateTimeField(blank=True, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
 
    class Meta:
        ordering = ['-published_at', '-created_at']
 
    def __str__(self): return self.title
 
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.title)
        super().save(*args, **kwargs)
 
