travel_backend/
├── app/
│   ├── main.py                  # app setup, CORS, router wiring
│   ├── core/
│   │   ├── config.py            # env settings (DB, cache, Cloudinary, site info)
│   │   ├── security.py          # JWT + password hashing
│   │   ├── redis_client.py      # fail-soft cache: auto-disables if Redis is unreachable
│   │   └── slugify.py           # slug generation for packages/destinations/blog posts
│   ├── db/
│   │   ├── database.py          # SQLAlchemy engine/session
│   │   └── base.py              # Base class import hub
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── package.py           # + slug
│   │   ├── testimonial.py       # image is {url, public_id}
│   │   ├── faq.py
│   │   ├── most_visited.py      # + slug, image is {url, public_id}
│   │   ├── blog.py               # slug, status, SEO fields
│   │   ├── happy_moment.py
│   │   └── site_settings.py      # singleton row, Website Settings admin page
│   ├── schemas/                  # Pydantic models (mirrors models/)
│   ├── services/                 # business logic + caching
│   │   ├── auth_service.py
│   │   ├── package_service.py
│   │   ├── testimonial_service.py
│   │   ├── faq_service.py
│   │   ├── most_visited_service.py
│   │   ├── blog_service.py
│   │   ├── happy_moment_service.py
│   │   ├── site_settings_service.py
│   │   └── upload_service.py        # Cloudinary uploads, returns {url, public_id}
│   └── routes/                   # API endpoints (mirrors services/, plus:)
│       ├── auth_routes.py
│       ├── admin_routes.py       # admin-only: manage creators
│       └── upload_routes.py      # POST /uploads/image
├── requirements.txt
└── .env.example

Public endpoints: /packages, /packages/slug/{slug}, /most-visited,
/most-visited/slug/{slug}, /testimonials, /faqs, /blogs, /blogs/slug/{slug},
/happy-moments, /settings.

Admin endpoints (mirror the above under /admin, plus /admin/creators and
POST /uploads/image) require a logged-in admin or creator; a few
(/settings/admin, /admin/creators) require the admin role specifically.

Images: uploaded via POST /uploads/image, stored on Cloudinary, returned
as {url, public_id}. Set CLOUDINARY_CLOUD_NAME/API_KEY/API_SECRET in .env
(from your Cloudinary dashboard) - uploads return a clear error until
those are set, rather than failing silently.

Redis is optional and fails soft - the app runs identically with or
without it (see redis_client.py). Set CACHE_ENABLED=false to skip it
entirely.

Not included in this pass (kept out on request - can be added back
later): Leads/CRM, Batches, Branches, the admin dashboard stats
endpoint, and the Meta Conversions API integration. None of the
current frontend code calls these, so nothing is broken by their
absence.
