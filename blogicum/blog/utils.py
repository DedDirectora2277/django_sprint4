from django.utils import timezone


def filter_posts(posts):
    dt_now = timezone.now()
    posts = posts.filter(
        pub_date__lte=dt_now,
        is_published=True,
        category__is_published=True
    )
    return posts
