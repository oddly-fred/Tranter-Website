# core/views.py
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta

from geo_content.utils import get_content
from django.http import JsonResponse
from django.shortcuts import redirect
from django.http import HttpResponseRedirect


def home(request):
    # Load geo-specific content blocks
    hero_content = get_content('hero_section', request)
    cta_content = get_content('cta_banner', request)
    trust_content = get_content('trust_strip', request)

    # ── Sample data (replace with DB queries later)
    events = [
        {
            'title':    'Enterprise Tech Summit 2026',
            'date':     timezone.now() + timedelta(days=14),
            'location': 'Lagos' if request.is_nigeria else 'London',
        },
        {
            'title':    'Cybersecurity Workshop',
            'date':     timezone.now() + timedelta(days=28),
            'location': 'Virtual',
        },
        {
            'title':    'Zoho CRM Masterclass',
            'date':     timezone.now() + timedelta(days=45),
            'location': 'Abuja' if request.is_nigeria else 'Dubai',
        },
    ]

    insights = [
        {
            'title':     'Future of Enterprise IT in Africa',
            'category':  'Technology',
            'read_time': 8,
        },
        {
            'title':     'Zero Trust Security Guide',
            'category':  'Cybersecurity',
            'read_time': 6,
        },
        {
            'title':     'Digital Transformation ROI',
            'category':  'Strategy',
            'read_time': 5,
        },
    ]

    what_we_do = [
        {'name': 'IT Support Services',      'icon': '⚡', 'slug': 'it-support',       'accent': 'green'},
        {'name': 'Smart Solutions',           'icon': '🤖', 'slug': 'smart-solutions',  'accent': 'green'},
        {'name': 'Cybersecurity',             'icon': '🛡️', 'slug': 'cybersecurity',    'accent': 'red'},
        {'name': 'ManageEngine',              'icon': '📊', 'slug': 'manage-engine',    'accent': 'green'},
        {'name': 'Zoho Solutions',            'icon': '☁️', 'slug': 'zoho-solutions',   'accent': 'red'},
        {'name': 'Digital Marketing & Brand', 'icon': '🌐', 'slug': 'digital-marketing','accent': 'green'},
        {'name': 'HR Support Services',       'icon': '👥', 'slug': 'hr-support',       'accent': 'red'},
        {'name': 'Business Process Outsourcing','icon':'⚙️','slug': 'bpo',              'accent': 'green'},
        {'name': 'Website Development',       'icon': '💻', 'slug': 'website-dev',      'accent': 'red'},
    ]

    # Region-specific clients
    if request.is_nigeria:
        clients = [
            'GTBank', 'Zenith Bank', 'FCMB', 'UBA', 'FBNQuest', 'Stanbic IBTC',
            'Fidelity Bank', 'Air Peace', 'DBN', 'Bank of Industry',
            'Sterling Bank', 'Heritage Bank', 'Wema Bank', 'Union Bank',
            'Keystone Bank', 'Jaiz Bank', 'TajBank', 'FSDH Merchant',
        ]
    else:
        clients = [
            'HSBC', 'Barclays', 'Standard Chartered', 'Deutsche Bank',
            'Shell', 'BP', 'TotalEnergies', 'ExxonMobil',
            'Unilever', 'Nestlé', 'Procter & Gamble', 'Coca-Cola',
            'Microsoft', 'Google', 'Amazon', 'IBM',
            'Siemens', 'GE', 'Honeywell', 'Schneider Electric',
        ]

    context = {
        'page_title': 'Home',
        'events':     events,
        'insights':   insights,
        'what_we_do':   what_we_do,
        'clients':    clients,
        # Geo content blocks
        'hero_content':  hero_content,
        'cta_content':   cta_content,
        'trust_content': trust_content,
    }
    return render(request, 'home.html', context)



def events(request):
    return render(request, 'core/events.html', {'page_title': 'Events'})


def insights(request):
    return render(request, 'core/insights.html', {'page_title': 'Insights'})


# ── ADD/REPLACE in core/views.py ─────────────────────────────────────────

def contact(request):
    """
    Contact page view.
    Handles both GET (show form) and POST (process submission).
    When using Zoho iframe instead of Django form,
    simplify to just: return render(request, 'core/contact.html', context)
    """
    success    = False
    is_nigeria = getattr(request, 'is_nigeria', True)
 
    if request.method == 'POST':
        # Collect form data
        first_name   = request.POST.get('first_name', '').strip()
        last_name    = request.POST.get('last_name', '').strip()
        email        = request.POST.get('email', '').strip()
        phone        = request.POST.get('phone', '').strip()
        company      = request.POST.get('company', '').strip()
        service      = request.POST.get('service', '').strip()
        message      = request.POST.get('message', '').strip()
        inquiry_type = request.POST.get('inquiry_type', 'general').strip()
 
        # Basic server-side validation
        if first_name and email and company and message:
            # ── Save to DB (uncomment when ConsultationRequest model exists)
            # from .models import ConsultationRequest
            # ConsultationRequest.objects.create(
            #     first_name=first_name, last_name=last_name,
            #     email=email, phone=phone, organisation=company,
            #     service=service, message=message,
            #     source_page='/contact/',
            # )
 
            # ── Optional: send email notification
            # from django.core.mail import send_mail
            # send_mail(
            #     subject=f'New Contact: {first_name} {last_name} — {company}',
            #     message=f'From: {email}\n\n{message}',
            #     from_email='noreply@tranter.com.ng',
            #     recipient_list=['info@tranter.com.ng'],
            #     fail_silently=True,
            # )
 
            success = True
 
    return render(request, 'core/contact.html', {
        'page_title': 'Contact Us',
        'is_nigeria': is_nigeria,
        'success':    success,
    })



def who_we_are(request):
    return render(request, 'core/who_we_are.html', {'page_title': 'Who We Are'})


# core/views.py — SERVICES_DATA section
# Paste SERVICES_DATA and the two view functions into your core/views.py

# core/views.py — SERVICES_DATA section
# Paste SERVICES_DATA and the two view functions into your core/views.py

SERVICES_DATA = [
    {
        "slug":    "it-support",
        "icon":    "⚡",
        "accent":  "green",
        "number":  "01",
        "name":    "IT Support Services",
        "tagline": "Always-on infrastructure. Zero compromise.",

        # ── Copy shown to both regions (short card description)
        "short": "This capability focuses on building and managing the digital backbone of modern organizations, ensuring systems perform reliably across geographies and operating environments.",

        # ── Nigeria-specific content
        "ng": {
            "headline":  "Enterprise IT Support — Built for Nigeria",
            "body":      "We provide on-site and remote IT support across Lagos, Abuja, Port Harcourt and 20+ locations. Our engineers manage the full infrastructure stack — helpdesk, networks, servers and endpoints — with SLAs calibrated to Nigerian enterprise operations.",
            "note":      "On-site engineers available across Lagos, Abuja and Port Harcourt. We understand the local infrastructure challenges.",
            "cta":       "Get Nigeria IT Support",
            "tags":      ["Lagos", "Abuja", "Port Harcourt", "24/7 NOC"],
        },

        # ── Global content
        "global": {
            "headline":  "Managed IT Services — Global Delivery",
            "body":      "We design and operate enterprise IT infrastructure through a distributed global delivery model — remote-first with on-site escalation across key markets. Our certified engineers manage your full environment to international SLA standards.",
            "note":      "Remote-first delivery with on-site escalation across Africa, UK and the Middle East.",
            "cta":       "Get Global IT Support",
            "tags":      ["Remote-first", "Multi-timezone", "ISO 20000"],
        },

        "features": [
            "24/7 Helpdesk & NOC Support",
            "End-user device management",
            "Network design & deployment",
            "Server & data centre management",
            "SLA-driven incident response",
            "Proactive monitoring & alerting",
        ],
        "sla": "99% uptime SLA",
    },
    {
        "slug":    "smart-solutions",
        "icon":    "🤖",
        "accent":  "green",
        "number":  "02",
        "name":    "Smart Solutions",
        "tagline": "From manual to intelligent — at scale.",
        "short":   "This capability enables organizations to shift from manual operations to intelligent, technology-enabled workflows that scale without adding headcount.",

        "ng": {
            "headline": "Smart Automation for Nigerian Enterprises",
            "body":     "We deploy intelligent automation and IoT solutions tailored for Nigerian banking, energy, manufacturing and public sector environments — designed to work within local infrastructure constraints while delivering world-class operational efficiency.",
            "note":     "Proven deployments across Nigerian banking, energy and manufacturing sectors.",
            "cta":      "Explore Smart Solutions in Nigeria",
            "tags":     ["Banking", "Energy", "Manufacturing", "Lagos-based team"],
        },
        "global": {
            "headline": "Enterprise Automation — Global Scale",
            "body":     "We design and deploy smart automation, IoT integrations and AI-powered workflows for global enterprises. From process automation to intelligent analytics — we build systems that turn your operational data into competitive advantage.",
            "note":     "Global delivery with cross-industry automation frameworks and remote implementation.",
            "cta":      "Explore Smart Solutions Globally",
            "tags":     ["IoT", "AI workflows", "RPA", "Global delivery"],
        },

        "features": [
            "Business process automation (BPA)",
            "IoT sensor integration & monitoring",
            "AI-powered analytics & dashboards",
            "Robotic Process Automation (RPA)",
            "ERP and CRM integrations",
            "Custom workflow design",
        ],
        "sla": "Guaranteed milestones",
    },
    {
        "slug":    "cybersecurity",
        "icon":    "🛡️",
        "accent":  "red",
        "number":  "03",
        "name":    "Cybersecurity",
        "tagline": "Security as infrastructure — not an afterthought.",
        "short":   "This capability embeds security into business operations, not as an afterthought, protecting your organisation across every layer.",

        "ng": {
            "headline": "Cybersecurity for Nigerian Organisations",
            "body":     "We deliver NITDA-aligned cybersecurity programmes for Nigerian financial institutions, government agencies and enterprises. Our local team understands the Nigerian threat landscape and regulatory environment — from CBN cybersecurity frameworks to NDPR compliance.",
            "note":     "NITDA-aligned and CBN cybersecurity framework compliance support for Nigerian organisations.",
            "cta":      "Secure Your Nigerian Operations",
            "tags":     ["NITDA aligned", "CBN framework", "NDPR", "Local SOC team"],
        },
        "global": {
            "headline": "Enterprise Cybersecurity — Global Standards",
            "body":     "We deliver intelligence-led cybersecurity protection combining world-class tooling with certified engineers. From Zero Trust architecture to SOC-as-a-Service — we keep your organisation ahead of threats across all jurisdictions.",
            "note":     "GDPR, ISO 27001 and SOC 2 compliance advisory for international operations.",
            "cta":      "Secure Your Global Operations",
            "tags":     ["ISO 27001", "GDPR", "SOC 2", "Zero Trust"],
        },

        "features": [
            "Penetration testing & vulnerability assessment",
            "Security Operations Centre (SOC) as a Service",
            "Zero Trust architecture design",
            "Endpoint Detection & Response (EDR)",
            "ISO 27001 compliance advisory",
            "Incident response & forensics",
        ],
        "sla": "< 2hr incident response",
    },
    {
        "slug":    "hr-support",
        "icon":    "👥",
        "accent":  "red",
        "number":  "04",
        "name":    "HR Support Services",
        "tagline": "People operations — systemised and scalable.",
        "short":   "This capability supports leadership teams in optimizing workforce operations across distributed environments with technology-enabled HR systems.",

        "ng": {
            "headline": "HR Support for Nigerian Businesses",
            "body":     "We design and operate HR support systems built for the Nigerian regulatory environment — covering PENCOM, NSITF, ITF and Nigerian labour law compliance. Our team supports workforce operations across single and multi-site Nigerian enterprises.",
            "note":     "Nigerian labour law, PENCOM and NSITF regulatory compliance support included.",
            "cta":      "Get HR Support in Nigeria",
            "tags":     ["PENCOM", "NSITF", "Labour law", "Payroll ₦"],
        },
        "global": {
            "headline": "Global HR Operations Support",
            "body":     "We manage workforce operations across multiple jurisdictions — combining technology platforms with specialist HR advisory for distributed enterprise teams. From UK employment law to multi-territory payroll processing.",
            "note":     "Multi-jurisdiction HR compliance across Africa, UK and the Middle East.",
            "cta":      "Get Global HR Support",
            "tags":     ["Multi-jurisdiction", "UK employment law", "Global payroll"],
        },

        "features": [
            "HR system implementation & support",
            "Payroll processing & compliance",
            "Recruitment process outsourcing",
            "Employee onboarding systems",
            "Performance management frameworks",
            "Labour law compliance advisory",
        ],
        "sla": "Dedicated HR manager",
    },
    {
        "slug":    "digital-marketing",
        "icon":    "🌐",
        "accent":  "green",
        "number":  "05",
        "name":    "Digital Marketing & Brand Development",
        "tagline": "Enterprise-grade digital presence that converts.",
        "short":   "This capability focuses on building enterprise-grade digital presence aligned to business growth, not vanity metrics.",

        "ng": {
            "headline": "Digital Marketing for Nigerian Brands",
            "body":     "We build and scale digital presence for Nigerian enterprises across the channels that matter — Google search, Meta, LinkedIn and local platforms. Our campaigns are calibrated for Nigerian audiences, Naira budgets and local market dynamics.",
            "note":     "Market-specific campaigns across Lagos, Abuja, PH and other Nigerian cities. NGN budgets.",
            "cta":      "Grow Your Nigerian Digital Presence",
            "tags":     ["Lagos market", "NGN budgets", "Local SEO", "Meta Nigeria"],
        },
        "global": {
            "headline": "Global Digital Marketing & Brand",
            "body":     "We position enterprise brands for measurable growth across international digital channels — from brand strategy and SEO to paid media and conversion-optimised content. Real pipeline and brand authority, not vanity metrics.",
            "note":     "Multi-market campaigns calibrated for international brand positioning and USD budgets.",
            "cta":      "Grow Your Global Digital Presence",
            "tags":     ["International SEO", "USD budgets", "Multi-market", "Brand strategy"],
        },

        "features": [
            "Brand strategy & identity",
            "Search Engine Optimisation (SEO)",
            "Paid media — Google & Meta",
            "Content strategy & production",
            "Social media management",
            "Analytics & conversion optimisation",
        ],
        "sla": "Monthly performance reports",
    },
    {
        "slug":    "bpo",
        "icon":    "⚙️",
        "accent":  "green",
        "number":  "06",
        "name":    "Business Process Outsourcing",
        "tagline": "Non-core functions — turned into competitive advantage.",
        "short":   "This capability designs and manages outsourced operations, turning non-core functions into scalable, technology-enabled systems with measurable SLA performance.",

        "ng": {
            "headline": "BPO Services — Built for Nigerian Enterprises",
            "body":     "We operate non-core business functions for Nigerian enterprises with dedicated on-site teams in Lagos and Abuja. Our BPO delivery combines local sector knowledge in banking, telco and FMCG with technology-enabled operations management.",
            "note":     "Nigeria-based BPO teams with deep sector knowledge in banking, telco and FMCG.",
            "cta":      "Outsource in Nigeria",
            "tags":     ["Banking BPO", "Telco BPO", "Lagos-based teams", "NGN SLAs"],
        },
        "global": {
            "headline": "Global BPO — Offshore Managed Operations",
            "body":     "We take ownership of your non-core functions and operate them as managed services — with defined SLAs, dedicated teams and continuous improvement built in. Full data protection compliance across all delivery locations.",
            "note":     "Offshore delivery centres with full GDPR and data protection compliance.",
            "cta":      "Outsource Globally",
            "tags":     ["GDPR compliant", "Offshore delivery", "SLA-backed", "Multi-timezone"],
        },

        "features": [
            "Back-office operations management",
            "Customer service & support (voice, chat, email)",
            "Finance & accounting processing",
            "Data entry & document management",
            "Quality assurance & reporting",
            "SLA-governed managed service delivery",
        ],
        "sla": "SLA-backed operations",
    },
    {
        "slug":    "website-development",
        "icon":    "💻",
        "accent":  "red",
        "number":  "07",
        "name":    "Website Development & Optimisation",
        "tagline": "Your website is infrastructure — build it that way.",
        "short":   "This capability positions digital assets as operational infrastructure, not marketing tools — performance-driven, conversion-optimised and built to scale.",

        "ng": {
            "headline": "Website Development for Nigerian Businesses",
            "body":     "We design and build enterprise websites and web applications for Nigerian organisations — with local hosting options on Nigerian data centres, .ng domain support and sites optimised for Nigerian internet infrastructure and mobile-first audiences.",
            "note":     "Local hosting on Nigerian data centres available. .ng domain support included.",
            "cta":      "Build Your Nigerian Website",
            "tags":     ["Nigerian hosting", ".ng domains", "Mobile-first", "NGN pricing"],
        },
        "global": {
            "headline": "Global Website Development",
            "body":     "We build enterprise websites and web applications that perform internationally — fast, secure, accessible and deployed on global CDN infrastructure. GDPR-compliant hosting options available across multiple regions.",
            "note":     "Global CDN deployment with GDPR-compliant hosting options across multiple regions.",
            "cta":      "Build Your Global Website",
            "tags":     ["Global CDN", "GDPR hosting", "Core Web Vitals", "99.9% uptime"],
        },

        "features": [
            "Custom website design & development",
            "E-commerce platforms",
            "Web application development",
            "CMS implementation (Django, WordPress)",
            "Performance optimisation & Core Web Vitals",
            "Hosting, security & maintenance",
        ],
        "sla": "99.9% hosting uptime",
    },
]


# ── Stats — geo-aware ─────────────────────────────
STATS_NG = [
    {"value": "99",  "suffix": "%",  "label": "SLA completion across all support sites",     "accent": "green"},
    {"value": "350", "suffix": "+",  "label": "Expert ICT & Smart Solutions Engineers",      "accent": "red"},
    {"value": "40",  "suffix": "+",  "label": "Global OEM Partners across the Globe",        "accent": "green"},
    {"value": "60",  "suffix": "+",  "label": "Channel Partners around the World",           "accent": "red"},
]
STATS_GLOBAL = [
    {"value": "99",  "suffix": "%",  "label": "SLA completion across all client sites",      "accent": "green"},
    {"value": "350", "suffix": "+",  "label": "Certified engineers across global teams",     "accent": "red"},
    {"value": "40",  "suffix": "+",  "label": "OEM partners across all service lines",       "accent": "green"},
    {"value": "60",  "suffix": "+",  "label": "Channel partners in key global markets",      "accent": "red"},
]

# ── Why Tranter pillars ───────────────────────────
WHY_PILLARS = [
    {
        "num": "01", "accent": "green",
        "title": "Global Delivery Model",
        "ng":     "Distributed workforce delivering services on-site and remotely across Lagos, Abuja, Port Harcourt and 20+ locations in Nigeria.",
        "global": "Distributed workforce delivering services remotely and on-site across multiple international markets.",
    },
    {
        "num": "02", "accent": "red",
        "title": "Enterprise-Grade Operations",
        "ng":     "ISO-certified processes and SLA-driven performance designed for Nigerian enterprise environments and regulatory requirements.",
        "global": "ISO-certified processes and SLA-driven performance ensuring reliability and scalability at global enterprise scale.",
    },
    {
        "num": "03", "accent": "green",
        "title": "Strategic Partner Mindset",
        "ng":     "We operate as long-term partners to Nigerian businesses — not transactional vendors. Your operational success is our metric.",
        "global": "We collaborate with leadership teams globally to design and manage technology systems that drive long-term efficiency.",
    },
    {
        "num": "04", "accent": "red",
        "title": "Operational Depth",
        "ng":     "Decades of experience deploying and managing enterprise technology across Nigeria's most demanding sectors.",
        "global": "Extensive experience designing and managing enterprise technology across complex, regulated global industries.",
    },
    {
        "num": "05", "accent": "green",
        "title": "Scalable Engagement",
        "ng":     "Engagement models that scale with your business — from SME to large enterprise across the Nigerian market.",
        "global": "Flexible engagement models that scale with your business across geographies and growth stages.",
    },
]

# ── FAQ — geo-aware ───────────────────────────────
FAQS_NG = [
    {
        "q": "What does Tranter specialise in?",
        "a": "Tranter specialises in enterprise IT infrastructure, cybersecurity, smart automation, managed services and digital transformation for organisations across Nigeria and Africa.",
    },
    {
        "q": "Does Tranter operate across Nigeria?",
        "a": "Yes. We have on-the-ground teams in Lagos, Abuja and Port Harcourt, with service coverage across 20+ locations in Nigeria.",
    },
    {
        "q": "What industries do you serve in Nigeria?",
        "a": "We serve financial services, banking, energy, manufacturing, logistics, healthcare, education and public sector organisations across Nigeria.",
    },
    {
        "q": "Do you provide managed IT services in Nigeria?",
        "a": "Yes. We provide fully managed IT services with local engineers, 24/7 NOC support and SLAs tailored to Nigerian enterprise environments.",
    },
    {
        "q": "Can Tranter support enterprise-level Nigerian organisations?",
        "a": "Yes. Our client portfolio includes major Nigerian banks, energy companies and public sector institutions operating at enterprise scale.",
    },
    {
        "q": "What makes Tranter different from other IT providers in Nigeria?",
        "a": "We combine global standards with local presence — ISO-certified operations, on-site engineers and deep knowledge of the Nigerian regulatory and infrastructure landscape.",
    },
]
FAQS_GLOBAL = [
    {
        "q": "What does Tranter specialise in?",
        "a": "Tranter specialises in enterprise IT infrastructure, cybersecurity, smart automation, managed services and digital transformation for organisations globally.",
    },
    {
        "q": "Does Tranter operate globally?",
        "a": "Yes. We operate a distributed global delivery model across Africa, the UK and the Middle East — remote-first with on-site capability in key markets.",
    },
    {
        "q": "What industries do you serve globally?",
        "a": "We serve financial services, energy, manufacturing, logistics, healthcare, education and regulated industries across international markets.",
    },
    {
        "q": "Do you provide managed IT services internationally?",
        "a": "Yes. We deliver fully managed IT services through our global delivery model with certified engineers operating to international SLA standards.",
    },
    {
        "q": "Can Tranter support large international organisations?",
        "a": "Yes. We are experienced in delivering enterprise technology programmes for complex international organisations across multiple markets and regulatory environments.",
    },
    {
        "q": "What makes Tranter different from other global IT providers?",
        "a": "We combine global delivery standards with genuine local expertise — ISO-certified operations, sector-specific knowledge and a strategic partner mindset rather than a transactional vendor approach.",
    },
]

def what_we_do(request):
    is_nigeria = getattr(request, 'is_nigeria', True)

    if is_nigeria:
        services = [s for s in SERVICES_DATA if s.get('ng')]
    else:
        services = [s for s in SERVICES_DATA if s.get('global')]

    return render(request, "core/what_we_do.html", {
        'page_title': 'What We Do',
        'what_we_do': services,
        'stats': STATS_NG if is_nigeria else STATS_GLOBAL,
        'pillars': WHY_PILLARS,
        'faqs': FAQS_NG if is_nigeria else FAQS_GLOBAL,
        'is_nigeria': is_nigeria,
    })

def service_detail(request, slug):
    from django.http import Http404
    from django.shortcuts import redirect

    service = next((s for s in SERVICES_DATA if s['slug'] == slug), None)
    
    if not service:
        raise Http404

    is_nigeria = getattr(request, 'is_nigeria', True)

    # 🚨 GEO ACCESS CONTROL
    if is_nigeria:
        if not service.get('ng'):
            return redirect('core:service_detail', slug=slug)  # or what_we_do
    else:
        if not service.get('global'):
            return redirect('core:service_detail', slug=slug)  # or what_we_do

    related = [s for s in SERVICES_DATA if s['slug'] != slug][:3]

    return render(request, 'core/service_detail.html', {
        'page_title': service['name'],
        'service': service,
        'related': related,
        'is_nigeria': is_nigeria,
        'geo': service['ng'] if is_nigeria else service['global'],
    })



# Paste into core/views.py — append at the bottom
# These functions handle /events/ and /events/<slug>/

from django.shortcuts import render
from django.utils import timezone

# ══════════════════════════════════════════════════
# DUMMY DATA — replace with DB queries after migration
# ══════════════════════════════════════════════════

DUMMY_EVENTS = [
    {
        "id": 1,
        "slug": "enterprise-cybersecurity-summit-2026",
        "title": "Enterprise Cybersecurity Summit 2026",
        "tagline": "Protecting the Modern Nigerian Enterprise",
        "event_type": "conference", "type_label": "Conference",
        "status": "upcoming", "access": "all",
        "date_display": "15 April 2026", "time_display": "9:00 AM WAT",
        "date_iso": "2026-04-15T09:00:00",
        "location": "Eko Hotel & Suites, Victoria Island, Lagos",
        "is_online": False, "is_featured": True, "is_free": False,
        "price_ng": "₦25,000", "price_global": "$35",
        "registration_url": "https://zoom.us/webinar/register",
        "cover": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1600&q=80",
        "banner": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1920&q=80",
        "description": "Nigeria's premier enterprise cybersecurity event — bringing together CISOs, IT leaders and security professionals to tackle the biggest threats facing African enterprises in 2026.",
        "tags": ["Cybersecurity", "Conference", "In-Person"], "accent": "red",
        "attendees_expected": 500,
        "speakers": [
            {"name": "Adebayo Okonkwo", "role": "CISO, Zenith Bank"},
            {"name": "Dr. Fatima Aliyu", "role": "Head of Security, CBN"},
            {"name": "James Thorne",     "role": "VP Security, Microsoft Africa"},
        ],
    },
    {
        "id": 2,
        "slug": "zoho-crm-masterclass-april",
        "title": "Zoho CRM Masterclass",
        "tagline": "Build a Sales Machine in 90 Minutes",
        "event_type": "webinar", "type_label": "Webinar",
        "status": "upcoming", "access": "all",
        "date_display": "22 April 2026", "time_display": "2:00 PM WAT",
        "date_iso": "2026-04-22T14:00:00",
        "location": "Online — Zoom", "is_online": True,
        "is_featured": False, "is_free": True,
        "price_ng": "Free", "price_global": "Free",
        "registration_url": "https://zoom.us/webinar/register",
        "cover": "https://images.unsplash.com/photo-1551434678-e076c223a692?w=800&q=80",
        "banner": "",
        "description": "A hands-on masterclass covering Zoho CRM setup, pipeline automation and sales reporting. Perfect for sales managers and operations leaders.",
        "tags": ["Zoho", "CRM", "Webinar", "Free"], "accent": "green",
        "attendees_expected": 200,
        "speakers": [
            {"name": "Chukwuemeka Eze", "role": "Zoho Solutions Lead, Tranter IT"},
        ],
    },
    {
        "id": 3,
        "slug": "digital-transformation-workshop-may",
        "title": "Digital Transformation Workshop",
        "tagline": "From Legacy to Intelligent Operations",
        "event_type": "workshop", "type_label": "Workshop",
        "status": "upcoming", "access": "ng",
        "date_display": "8 May 2026", "time_display": "10:00 AM WAT",
        "date_iso": "2026-05-08T10:00:00",
        "location": "Tranter HQ, Victoria Island, Lagos",
        "is_online": False, "is_featured": False, "is_free": False,
        "price_ng": "₦15,000", "price_global": "$20",
        "registration_url": "https://zoom.us/webinar/register",
        "cover": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&q=80",
        "banner": "",
        "description": "A full-day workshop for IT managers ready to accelerate their digital transformation journey. Includes live demos, case studies and Q&A.",
        "tags": ["Workshop", "IT", "Lagos", "In-Person"], "accent": "green",
        "attendees_expected": 80,
        "speakers": [],
    },
    {
        "id": 4,
        "slug": "global-it-infrastructure-webinar",
        "title": "Global IT Infrastructure Trends 2026",
        "tagline": "What Enterprise IT Looks Like in 5 Years",
        "event_type": "webinar", "type_label": "Webinar",
        "status": "upcoming", "access": "global",
        "date_display": "20 May 2026", "time_display": "3:00 PM GMT",
        "date_iso": "2026-05-20T15:00:00",
        "location": "Online — Zoom", "is_online": True,
        "is_featured": False, "is_free": True,
        "price_ng": "Free", "price_global": "Free",
        "registration_url": "https://zoom.us/webinar/register",
        "cover": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80",
        "banner": "",
        "description": "International panel on cloud infrastructure, AI-driven IT operations and the future of enterprise technology delivery — for global enterprise leaders.",
        "tags": ["Global", "Cloud", "Webinar", "Free"], "accent": "green",
        "attendees_expected": 300,
        "speakers": [
            {"name": "Sarah Mitchell", "role": "Head of Cloud, Tranter Global"},
        ],
    },
    {
        "id": 5,
        "slug": "tranter-tech-summit-2025",
        "title": "Tranter Tech Summit 2025",
        "tagline": "The Future of Enterprise Technology in Africa",
        "event_type": "conference", "type_label": "Conference",
        "status": "past", "access": "all",
        "date_display": "14 November 2025", "time_display": "9:00 AM WAT",
        "date_iso": "2025-11-14T09:00:00",
        "location": "Landmark Centre, Victoria Island, Lagos",
        "is_online": False, "is_featured": False, "is_free": False,
        "price_ng": "₦20,000", "price_global": "$30",
        "registration_url": "",
        "cover": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&q=80",
        "banner": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1920&q=80",
        "video_recap": "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "description": "Our flagship annual conference — 400+ IT professionals, 20 speakers and 15 technology partners for a full day of insights and networking.",
        "tags": ["Conference", "Annual", "Lagos", "Flagship"], "accent": "red",
        "attendees_count": 412, "partners_count": 15,
        "speakers_count": 20, "sessions_count": 12,
        "gallery": [
            {"url": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=600&q=80", "size": "large"},
            {"url": "https://images.unsplash.com/photo-1505373877841-8d25f7d46678?w=600&q=80", "size": "small"},
            {"url": "https://images.unsplash.com/photo-1515187029135-18ee286d815b?w=600&q=80", "size": "medium"},
            {"url": "https://images.unsplash.com/photo-1591115765373-5207764f72e7?w=600&q=80", "size": "small"},
            {"url": "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=600&q=80", "size": "medium"},
            {"url": "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=600&q=80", "size": "large"},
        ],
        "speakers": [
            {"name": "Olumide Afolabi", "role": "CEO, Tranter IT"},
            {"name": "Dr. Ngozi Eke",   "role": "Director, NITDA"},
        ],
    },
    {
        "id": 6,
        "slug": "cybersecurity-awareness-webinar-2025",
        "title": "Cybersecurity Awareness Webinar",
        "tagline": "Defend Your Business from Modern Threats",
        "event_type": "webinar", "type_label": "Webinar",
        "status": "past", "access": "all",
        "date_display": "5 September 2025", "time_display": "2:00 PM WAT",
        "date_iso": "2025-09-05T14:00:00",
        "location": "Online — Zoom", "is_online": True,
        "is_featured": False, "is_free": True,
        "price_ng": "Free", "price_global": "Free",
        "registration_url": "",
        "cover": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=800&q=80",
        "banner": "",
        "video_recap": "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "description": "A 2-hour deep dive into cybersecurity threats targeting African enterprises — with live demonstrations and Q&A with our security team.",
        "tags": ["Cybersecurity", "Webinar", "Free"], "accent": "red",
        "attendees_count": 280, "partners_count": 3,
        "speakers_count": 4, "sessions_count": 3,
        "gallery": [],
        "speakers": [],
    },
]

DUMMY_TESTIMONIALS = [
    {
        "name":   "Adaeze Okonkwo",
        "role":   "Head of IT, First Bank Nigeria",
        "quote":  "The Tranter Tech Summit was the most valuable event I attended in 2025. The quality of speakers and the level of peer networking was exceptional.",
        "rating": 5,
    },
    {
        "name":   "Emeka Nwosu",
        "role":   "CTO, Stanbic IBTC",
        "quote":  "The Zoho CRM Masterclass transformed how our sales team operates. Practical, insightful and immediately actionable. Highly recommended.",
        "rating": 5,
    },
    {
        "name":   "Fatima Hassan",
        "role":   "Operations Manager, Dangote Group",
        "quote":  "Finally an event that speaks to real challenges of Nigerian enterprise IT. Not theoretical — real solutions for real operating environments.",
        "rating": 5,
    },
    {
        "name":   "James Thorne",
        "role":   "VP Technology, Unilever Africa",
        "quote":  "World-class content delivered with genuine understanding of the African market. Tranter sets a new standard for enterprise events on the continent.",
        "rating": 5,
    },
]

EVENT_TYPES = [
    {"slug": "all",        "label": "All Events",  "icon": "📅"},
    {"slug": "conference", "label": "Conferences", "icon": "🏛️"},
    {"slug": "webinar",    "label": "Webinars",    "icon": "💻"},
    {"slug": "workshop",   "label": "Workshops",   "icon": "🔧"},
    {"slug": "training",   "label": "Training",    "icon": "📚"},
]


def _geo_visible(ev, is_nigeria):
    """Return True if this event should be shown to this user's region."""
    access = ev.get('access', 'all')
    if access == 'all':
        return True
    if access == 'ng' and is_nigeria:
        return True
    if access == 'global' and not is_nigeria:
        return True
    return False


def events(request):
    is_nigeria = getattr(request, 'is_nigeria', True)
    visible    = [ev for ev in DUMMY_EVENTS if _geo_visible(ev, is_nigeria)]

    # Featured — first upcoming featured, fallback to any upcoming
    featured = next(
        (ev for ev in visible if ev['status'] == 'upcoming' and ev.get('is_featured')),
        next((ev for ev in visible if ev['status'] == 'upcoming'), None)
    )
    upcoming     = [ev for ev in visible if ev['status'] == 'upcoming']
    past         = [ev for ev in visible if ev['status'] == 'past']
    past_gallery = [img for ev in past for img in ev.get('gallery', [])]

    return render(request, 'events.html', {
        'page_title':   'Events',
        'featured':     featured,
        'upcoming':     upcoming,
        'past':         past,
        'past_gallery': past_gallery,
        'testimonials': DUMMY_TESTIMONIALS,
        'event_types':  EVENT_TYPES,
        'is_nigeria':   is_nigeria,
    })


def event_detail(request, slug):
    is_nigeria = getattr(request, 'is_nigeria', True)
    event      = next((ev for ev in DUMMY_EVENTS if ev['slug'] == slug), None)
    if not event:
        from django.http import Http404
        raise Http404

    related = [e for e in DUMMY_EVENTS if e['slug'] != slug and e['status'] == event['status']][:3]
    price   = event.get('price_ng') if is_nigeria else event.get('price_global')

    return render(request, 'event_detail.html', {
        'page_title': event['title'],
        'event':      event,
        'related':    related,
        'price':      price or 'Free',
        'is_nigeria': is_nigeria,
    })







# Append to core/views.py
# ═══════════════════════════════════════════════════
# INSIGHTS — views + dummy data
# ═══════════════════════════════════════════════════

DUMMY_INSIGHTS = [
    {
        "id": 1,
        "slug": "future-of-enterprise-it-africa-2026",
        "title": "The Future of Enterprise IT in Africa: 2026 Outlook",
        "excerpt": "A deep analysis of how African enterprises are transforming their technology infrastructure — from legacy systems to cloud-native, AI-powered operations.",
        "body": "African enterprises are at a critical inflection point. The combination of mobile-first adoption, rising cloud infrastructure investment and a growing pool of local technology talent is creating conditions for rapid digital transformation unlike anything seen before on the continent. This report examines the key trends, challenges and opportunities shaping enterprise IT across Nigeria, Ghana, Kenya and South Africa through 2026 and beyond.",
        "insight_type": "article", "type_label": "Article", "type_icon": "📝",
        "category": "Technology", "category_slug": "technology",
        "audience": "ng",
        "tags": ["Cloud", "AI", "Enterprise", "Africa"],
        "author_name": "Olumide Afolabi", "author_role": "CEO, Tranter IT",
        "read_time": 8,
        "cover": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&q=80",
        "is_featured": True, "is_sponsored": False, "is_premium": False,
        "published_at": "March 15, 2026", "views": 2840, "likes": 142,
        "accent": "green",
    },
    {
        "id": 2,
        "slug": "zero-trust-security-guide-nigerian-banks",
        "title": "Zero Trust Security: A Practical Guide for Nigerian Banks",
        "excerpt": "How leading Nigerian financial institutions are implementing Zero Trust architecture to meet CBN cybersecurity requirements and protect customer data.",
        "body": "",
        "insight_type": "report", "type_label": "Report", "type_icon": "📊",
        "category": "Cybersecurity", "category_slug": "cybersecurity",
        "audience": "ng",
        "tags": ["Cybersecurity", "Banking", "Zero Trust", "CBN"],
        "author_name": "Dr. Fatima Aliyu", "author_role": "Head of Security Practice",
        "read_time": 12,
        "cover": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=800&q=80",
        "pdf_label": "Download Full Report",
        "is_featured": False, "is_sponsored": False, "is_premium": True,
        "published_at": "March 10, 2026", "views": 1920, "likes": 98,
        "accent": "red",
    },
    {
        "id": 3,
        "slug": "zoho-crm-roi-enterprise-case-study",
        "title": "How Enterprises Are Achieving 340% ROI with Zoho CRM",
        "excerpt": "A data-driven analysis of CRM adoption outcomes across 15 Nigerian enterprises — covering implementation timelines, sales uplift and operational savings.",
        "body": "",
        "insight_type": "article", "type_label": "Article", "type_icon": "📝",
        "category": "Strategy", "category_slug": "strategy",
        "audience": "all",
        "tags": ["Zoho", "CRM", "ROI", "Case Study"],
        "author_name": "Chukwuemeka Eze", "author_role": "Zoho Solutions Lead",
        "read_time": 6,
        "cover": "https://images.unsplash.com/photo-1551434678-e076c223a692?w=800&q=80",
        "is_featured": False, "is_sponsored": True, "is_premium": False,
        "published_at": "March 5, 2026", "views": 3100, "likes": 187,
        "accent": "green",
    },
    {
        "id": 4,
        "slug": "digital-transformation-roi-webinar-recap",
        "title": "Digital Transformation ROI: Webinar Recap & Key Takeaways",
        "excerpt": "Our most-attended webinar of 2025 — 280 enterprise leaders discussing measurable digital transformation outcomes across industries.",
        "body": "",
        "insight_type": "video", "type_label": "Video", "type_icon": "🎥",
        "category": "Technology", "category_slug": "technology",
        "audience": "all",
        "tags": ["Digital Transformation", "ROI", "Webinar"],
        "author_name": "Tranter Events Team", "author_role": "",
        "read_time": 45,
        "cover": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&q=80",
        "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "is_featured": False, "is_sponsored": False, "is_premium": False,
        "published_at": "Feb 28, 2026", "views": 1540, "likes": 76,
        "accent": "red",
    },
    {
        "id": 5,
        "slug": "manageengine-itsm-implementation-playbook",
        "title": "ManageEngine ITSM Implementation Playbook",
        "excerpt": "A step-by-step guide to deploying ManageEngine ServiceDesk Plus in enterprise environments — from scoping to go-live in 90 days.",
        "body": "",
        "insight_type": "report", "type_label": "Report", "type_icon": "📊",
        "category": "Technology", "category_slug": "technology",
        "audience": "all",
        "tags": ["ManageEngine", "ITSM", "Implementation", "Guide"],
        "author_name": "James Okonkwo", "author_role": "ITSM Practice Lead",
        "read_time": 15,
        "cover": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&q=80",
        "pdf_label": "Download Playbook",
        "is_featured": False, "is_sponsored": False, "is_premium": True,
        "published_at": "Feb 20, 2026", "views": 890, "likes": 54,
        "accent": "green",
    },
    {
        "id": 6,
        "slug": "hr-technology-trends-africa-2026",
        "title": "HR Technology Trends Shaping African Enterprises in 2026",
        "excerpt": "From payroll automation to AI-powered recruitment — how African enterprises are modernising their workforce operations through technology.",
        "body": "",
        "insight_type": "article", "type_label": "Article", "type_icon": "📝",
        "category": "Industry", "category_slug": "industry",
        "audience": "ng",
        "tags": ["HR Tech", "Payroll", "Africa", "Workforce"],
        "author_name": "Adaeze Obi", "author_role": "HR Practice Lead",
        "read_time": 7,
        "cover": "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=800&q=80",
        "is_featured": False, "is_sponsored": False, "is_premium": False,
        "published_at": "Feb 14, 2026", "views": 1230, "likes": 63,
        "accent": "red",
    },
    {
        "id": 7,
        "slug": "cloud-infrastructure-global-enterprise-guide",
        "title": "Cloud Infrastructure for Global Enterprise: 2026 Guide",
        "excerpt": "A comprehensive guide to building scalable, secure cloud infrastructure for international enterprises — covering AWS, Azure and hybrid approaches.",
        "body": "",
        "insight_type": "report", "type_label": "Report", "type_icon": "📊",
        "category": "Technology", "category_slug": "technology",
        "audience": "global",
        "tags": ["Cloud", "AWS", "Azure", "Global"],
        "author_name": "Sarah Mitchell", "author_role": "Head of Cloud, Tranter Global",
        "read_time": 18,
        "cover": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80",
        "pdf_label": "Download Cloud Guide",
        "is_featured": False, "is_sponsored": False, "is_premium": True,
        "published_at": "Feb 8, 2026", "views": 760, "likes": 41,
        "accent": "green",
    },
    {
        "id": 8,
        "slug": "bpo-cost-reduction-nigerian-enterprises",
        "title": "BPO as a Cost Reduction Strategy for Nigerian Enterprises",
        "excerpt": "How Nigerian companies are cutting operational costs by 35–60% through strategic outsourcing — a data-driven analysis with real case studies.",
        "body": "",
        "insight_type": "article", "type_label": "Article", "type_icon": "📝",
        "category": "Strategy", "category_slug": "strategy",
        "audience": "ng",
        "tags": ["BPO", "Cost Reduction", "Nigeria", "Operations"],
        "author_name": "Emeka Nwosu", "author_role": "BPO Practice Lead",
        "read_time": 9,
        "cover": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80",
        "is_featured": False, "is_sponsored": False, "is_premium": False,
        "published_at": "Jan 30, 2026", "views": 1480, "likes": 79,
        "accent": "red",
    },
]

INSIGHT_CATEGORIES = [
    {"slug": "all",           "label": "All",          "icon": "📄"},
    {"slug": "technology",    "label": "Technology",   "icon": "💻"},
    {"slug": "cybersecurity", "label": "Cybersecurity","icon": "🛡️"},
    {"slug": "strategy",      "label": "Strategy",     "icon": "🎯"},
    {"slug": "industry",      "label": "Industry",     "icon": "🏢"},
]

INSIGHT_TYPES = [
    {"slug": "all",     "label": "All Types", "icon": "📄"},
    {"slug": "article", "label": "Articles",  "icon": "📝"},
    {"slug": "report",  "label": "Reports",   "icon": "📊"},
    {"slug": "video",   "label": "Videos",    "icon": "🎥"},
]


def _insight_visible(ins, is_nigeria):
    a = ins.get('audience', 'all')
    if a == 'all': return True
    if a == 'ng' and is_nigeria: return True
    if a == 'global' and not is_nigeria: return True
    return False


def insights(request):
    is_nigeria  = getattr(request, 'is_nigeria', True)
    cat_filter  = request.GET.get('cat',  'all')
    type_filter = request.GET.get('type', 'all')
    q           = request.GET.get('q',    '').strip()

    visible = [i for i in DUMMY_INSIGHTS if _insight_visible(i, is_nigeria)]

    if cat_filter  != 'all': visible = [i for i in visible if i['category_slug'] == cat_filter]
    if type_filter != 'all': visible = [i for i in visible if i['insight_type']   == type_filter]
    if q:
        ql = q.lower()
        visible = [i for i in visible
                   if ql in i['title'].lower() or ql in i['excerpt'].lower()]

    featured = next((i for i in visible if i.get('is_featured')),
                    visible[0] if visible else None)
    rest     = [i for i in visible if not i.get('is_featured')]
    popular  = sorted(DUMMY_INSIGHTS, key=lambda x: x['views'], reverse=True)[:3]

    return render(request, 'insights_list.html', {
        'page_title':  'Insights',
        'featured':    featured,
        'insights':    rest,
        'popular':     popular,
        'categories':  INSIGHT_CATEGORIES,
        'types':       INSIGHT_TYPES,
        'is_nigeria':  is_nigeria,
        'active_cat':  cat_filter,
        'active_type': type_filter,
        'search_q':    q,
    })


def insight_detail(request, slug):
    from django.http import Http404
    is_nigeria = getattr(request, 'is_nigeria', True)
    insight    = next((i for i in DUMMY_INSIGHTS if i['slug'] == slug), None)
    if not insight: raise Http404

    related = [i for i in DUMMY_INSIGHTS
               if i['slug'] != slug
               and i['category_slug'] == insight['category_slug']][:3]

    return render(request, 'insight_detail.html', {
        'page_title': insight['title'],
        'insight':    insight,
        'related':    related,
        'is_nigeria': is_nigeria,
    })




def book_demo_popup(request):
    # Step 2a: Get user region (auto-detect via GET param or default to NG)
    region = request.GET.get("region", "NG").upper()
    
    # Step 2b: Fetch popup content based on region
    content = get_content(region=region, key="book_demo_popup")
    
    # Step 2c: Render modal template
    return render(request, "core/book_demo_popup.html", {"content": content})
    

def set_region(request):
    """
    Updates the 'region' session variable and redirects the user back.
    """
    # Get the region from the URL parameter (?region=NG or ?region=GLOBAL)
    region = request.GET.get('region', 'GLOBAL')
    
    # Save it in the session so it persists across all pages
    request.session['region'] = region
    
    # Redirect the user back to the page they were just on
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))