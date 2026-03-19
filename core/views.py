from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse

# Create your views here.

def home(request):
    return render(request, 'core/home.html', {'title': 'Home'})

def contact(request):
    return render(request, 'core/contact.html', {'title': 'Contact'})

def consultation_submit(request):
    if request.method == 'POST':
        # Handle form submission logic here
        messages.success(request, 'Your consultation request has been submitted successfully!')
        return redirect('home')
    return redirect('home')

def service_detail(request, slug):
    context = {
        'title': 'Service Detail',
        'slug': slug,
    }
    return render(request, 'core/service_detail.html', context)

def manage_engine(request):
    return render(request, 'core/manage_engine.html', {'title': 'ManageEngine'})

def services(request):
    return render(request, 'core/services.html', {'title': 'Services'})

def book_demo(request):
    return render(request, 'core/book_demo.html', {'title': 'Book a Demo'})

def zoho_solutions(request):
    return render(request, 'core/zoho_solutions.html', {'title': 'Zoho Solutions'})

def sector_detail(request, slug):
    context = {
        'title': 'Sector Detail',
        'slug': slug,
    }
    return render(request, 'core/sector_detail.html', context)


# ═══════════════════════════════════════════════════
# EVENTS VIEWS
# ═══════════════════════════════════════════════════

def events(request):
    """Events list page - simplified version without models."""
    # Sample featured event
    from datetime import datetime, timedelta
    featured_date = timezone.now() + timedelta(days=14)

    featured = {
        'title': 'Tranter Enterprise Technology Summit 2026',
        'description': 'Join industry leaders for a day of insights on enterprise technology transformation, cybersecurity best practices, and digital innovation strategies for the modern organization.',
        'date': featured_date,
        'location': 'Lagos, Nigeria',
        'is_online': False,
        'slug': 'enterprise-tech-summit-2026',
        'pk': 1,
        'cover_image': None,
        'registration_url': '#',
    }

    # Countdown data
    countdown_data = {
        'days': 14,
        'hours': 8,
        'minutes': 32,
        'seconds': 15,
        'target_iso': featured_date.isoformat(),
    }

    # Sample upcoming events
    upcoming = [
        {
            'title': 'Cybersecurity Workshop: Zero Trust Architecture',
            'description': 'Learn how to implement zero-trust security models in your organization.',
            'date': timezone.now() + timedelta(days=28),
            'location': 'Virtual',
            'is_online': True,
            'slug': 'cybersecurity-workshop-zero-trust',
            'cover_image': None,
        },
        {
            'title': 'Zoho CRM Implementation Masterclass',
            'description': 'Best practices for deploying Zoho CRM across enterprise teams.',
            'date': timezone.now() + timedelta(days=45),
            'location': 'Abuja, Nigeria',
            'is_online': False,
            'slug': 'zoho-crm-masterclass',
            'cover_image': None,
        },
        {
            'title': 'ITSM Excellence with ManageEngine',
            'description': 'Optimize your IT service management with proven strategies.',
            'date': timezone.now() + timedelta(days=60),
            'location': 'Virtual',
            'is_online': True,
            'slug': 'itsm-manageengine-excellence',
            'cover_image': None,
        },
    ]

    # Sample past events
    past = [
        {
            'title': 'Digital Transformation Forum 2025',
            'description': 'Exploring the latest trends in enterprise digital transformation.',
            'date': timezone.now() - timedelta(days=90),
            'slug': 'digital-transformation-forum-2025',
            'cover_image': None,
            'video_url': '#',
        },
        {
            'title': 'Cloud Infrastructure Summit',
            'description': 'Building scalable cloud infrastructure for African enterprises.',
            'date': timezone.now() - timedelta(days=120),
            'slug': 'cloud-infrastructure-summit',
            'cover_image': None,
            'video_url': None,
        },
        {
            'title': 'Cybersecurity Awareness Week',
            'description': 'Comprehensive security training for IT teams.',
            'date': timezone.now() - timedelta(days=180),
            'slug': 'cybersecurity-awareness-week',
            'cover_image': None,
            'video_url': '#',
        },
        {
            'title': 'Enterprise Automation Workshop',
            'description': 'Automating business processes for efficiency gains.',
            'date': timezone.now() - timedelta(days=210),
            'slug': 'enterprise-automation-workshop',
            'cover_image': None,
            'video_url': None,
        },
    ]

    context = {
        'title': 'Events',
        'featured': featured,
        'countdown_data': countdown_data,
        'upcoming': upcoming,
        'past': past,
    }
    return render(request, 'core/events_list.html', context)


def event_detail(request, slug):
    """Event detail page - simplified version."""
    from datetime import timedelta

    # Mock event based on slug
    event_date = timezone.now() + timedelta(days=14)
    event = {
        'title': 'Tranter Enterprise Technology Summit 2026',
        'description': 'Join industry leaders for a day of insights on enterprise technology transformation.',
        'date': event_date,
        'location': 'Lagos, Nigeria',
        'is_online': False,
        'slug': slug,
        'pk': 1,
        'content': '<p>Full event content goes here...</p>',
        'speakers': [],
        'agenda': [],
    }

    countdown_data = {
        'target_iso': event_date.isoformat(),
        'days': 14,
        'hours': 8,
        'minutes': 32,
        'seconds': 15,
    }

    related = []

    context = {
        'title': event['title'],
        'event': event,
        'countdown_data': countdown_data,
        'related': related,
    }
    return render(request, 'core/event_detail.html', context)


# ═══════════════════════════════════════════════════
# INSIGHTS VIEWS
# ═══════════════════════════════════════════════════

def insights(request):
    """Insights/Articles list page."""
    from datetime import timedelta

    # Categories
    categories = [
        {'slug': 'all', 'name': 'All Insights', 'active': True},
        {'slug': 'technology', 'name': 'Technology', 'active': False},
        {'slug': 'cybersecurity', 'name': 'Cybersecurity', 'active': False},
        {'slug': 'strategy', 'name': 'Strategy', 'active': False},
        {'slug': 'case-studies', 'name': 'Case Studies', 'active': False},
    ]

    # Hero/Featured article
    hero_article = {
        'title': 'The Future of Enterprise IT Infrastructure in Africa',
        'excerpt': 'How African enterprises are leapfrogging traditional IT constraints to build modern, cloud-native infrastructure that rivals global standards.',
        'category': {'name': 'Technology', 'slug': 'technology'},
        'published_at': timezone.now() - timedelta(days=3),
        'read_time': 8,
        'slug': 'future-enterprise-it-africa',
        'cover_image': None,
    }

    # Medium articles
    medium_articles = [
        {
            'title': 'Implementing Zero Trust Security',
            'excerpt': 'A practical guide to deploying zero-trust architectures in regulated industries.',
            'category': {'name': 'Cybersecurity', 'slug': 'cybersecurity'},
            'published_at': timezone.now() - timedelta(days=7),
            'slug': 'implementing-zero-trust',
        },
        {
            'title': 'Digital Transformation ROI Metrics',
            'excerpt': 'How to measure the real impact of your digital transformation initiatives.',
            'category': {'name': 'Strategy', 'slug': 'strategy'},
            'published_at': timezone.now() - timedelta(days=10),
            'slug': 'digital-transformation-roi',
        },
    ]

    # Small articles (sidebar)
    small_articles = [
        {
            'title': 'Zoho vs Salesforce: Enterprise Considerations',
            'category': {'name': 'Technology', 'slug': 'technology'},
            'published_at': timezone.now() - timedelta(days=5),
            'slug': 'zoho-vs-salesforce',
        },
        {
            'title': 'Managing Remote IT Teams',
            'category': {'name': 'Strategy', 'slug': 'strategy'},
            'published_at': timezone.now() - timedelta(days=12),
            'slug': 'managing-remote-it-teams',
        },
        {
            'title': 'ISO 27001 Certification Journey',
            'category': {'name': 'Case Studies', 'slug': 'case-studies'},
            'published_at': timezone.now() - timedelta(days=15),
            'slug': 'iso27001-certification-journey',
        },
        {
            'title': 'Cloud Cost Optimization Strategies',
            'category': {'name': 'Technology', 'slug': 'technology'},
            'published_at': timezone.now() - timedelta(days=18),
            'slug': 'cloud-cost-optimization',
        },
    ]

    # All articles grid
    all_articles = [
        {
            'title': 'Building Resilient IT Operations',
            'excerpt': 'Lessons from 15 years of enterprise IT service delivery.',
            'category': {'name': 'Case Studies', 'slug': 'case-studies'},
            'published_at': timezone.now() - timedelta(days=21),
            'read_time': 6,
            'slug': 'building-resilient-it-operations',
        },
        {
            'title': 'The State of Cybersecurity in Nigerian Banks',
            'excerpt': 'An analysis of current threats and defense strategies.',
            'category': {'name': 'Cybersecurity', 'slug': 'cybersecurity'},
            'published_at': timezone.now() - timedelta(days=25),
            'read_time': 10,
            'slug': 'cybersecurity-nigerian-banks',
        },
        {
            'title': 'Automation in HR Processes',
            'excerpt': 'How technology is transforming human resources management.',
            'category': {'name': 'Technology', 'slug': 'technology'},
            'published_at': timezone.now() - timedelta(days=30),
            'read_time': 5,
            'slug': 'automation-hr-processes',
        },
    ]

    context = {
        'title': 'Insights',
        'categories': categories,
        'hero_article': hero_article,
        'medium_articles': medium_articles,
        'small_articles': small_articles,
        'all_articles': all_articles,
    }
    return render(request, 'core/insights_list.html', context)


def insight_detail(request, slug):
    """Single insight/article detail page."""
    from datetime import timedelta

    article = {
        'title': 'The Future of Enterprise IT Infrastructure in Africa',
        'content': '<p>Full article content goes here...</p>',
        'category': {'name': 'Technology', 'slug': 'technology'},
        'published_at': timezone.now() - timedelta(days=3),
        'read_time': 8,
        'slug': slug,
    }

    context = {
        'title': article['title'],
        'article': article,
    }
    return render(request, 'core/insight_detail.html', context)


# ═══════════════════════════════════════════════════
# ADDITIONAL PAGE VIEWS
# ═══════════════════════════════════════════════════

def who_we_are(request):
    return render(request, 'core/who_we_are.html', {'title': 'Who We Are'})

def how_we_work(request):
    return render(request, 'core/how_we_work.html', {'title': 'How We Work'})

def global_reach(request):
    return render(request, 'core/global_reach.html', {'title': 'Global Reach'})

def sectors(request):
    return render(request, 'core/sectors.html', {'title': 'Sectors'})

def careers(request):
    return render(request, 'core/careers.html', {'title': 'Careers'})

def global_offices(request):
    return render(request, 'core/global_offices.html', {'title': 'Global Offices'})

def partner(request):
    return render(request, 'core/partner.html', {'title': 'Partner With Us'})

def support(request):
    return render(request, 'core/support.html', {'title': 'Support Portal'})

def privacy(request):
    return render(request, 'core/privacy.html', {'title': 'Privacy Policy'})

def terms(request):
    return render(request, 'core/terms.html', {'title': 'Terms of Service'})

def iso_certs(request):
    return render(request, 'core/iso_certs.html', {'title': 'ISO Certifications'})
