# Design Philosophy

*spatula* came out of several years of maintaining a very large,
community-driven scraper project, [Open States](https://openstates.org).

While several of the decisions made are best understood through this
lens, the goal of *spatula* is to remain lightweight so that even simple
projects can benefit from its structure.

## Common Problems

If you've written a few web scrapers, you're likely to have run into a
few common issues:

-   Scrapers are inherently messy as they tend to reflect the
    cleanliness (or lack thereof) of the underlying site.
-   Scrapers are often written and then left alone for months or years,
    only needing maintenance when the underlying site changes.
-   Some scrapes take hours to complete, making the development cycle
    for testing changes and fixes quite difficult.

## Goals

1.  **The framework should make it as easy as possible to get started
    and write clean scraper code.**

    While it is often easy, and tempting, to write a scraper as a dirty
    one-off script, spatula makes an attempt to provide an easy framework
    that most scrapers fit within without additional overhead.

    This reflects the reality that many scraper projects start small but grow
    quickly, so reaching for a heavyweight tool from the start often does
    not seem practical.

    The initial overhead imposed by the framework
    should be as light as possible, providing benefits even for authors
    that do not wish to use every feature available to them.

2.  **The framework should make it easy to read code that was written,
    with as many of the underlying assumptions of the scraper presented
    as clearly as possible for future maintenance.**

    By encouraging users to structure their scrapers in a readable way,
    scrapers will be easier to read later, and issues/maintenance can
    often be identified with specific components instead of forcing
    maintainers to comprehend a single gnarly script.

3.  **Iterative development of scrapers should be the norm.**

    It should be possible to test changes to a single part of the scrape
    without running the entire process. The user shouldn't have to
    comment out code or add temporary debug statements to do something
    that is extremely common when authoring scrapers.

4.  **Leverage modern Python to improve the experience.**

    There are some great things about Python 3 that we can leverage to
    make writing & maintaining scrapers easier.

    To that end, *spatula* is fully type-annotated, and integrates well with
    [`dataclasses`](https://docs.python.org/3/library/dataclasses.html),
    [`attrs`](https://www.attrs.org/en/stable/),
    and [`pydantic`](https://pydantic-docs.helpmanual.io/).

## Pages & Page Roles

A key component of using **spatula** is thinking of the scraper in terms
of types of "pages".

For each type of page you encounter, you'll write a subclass of
`Page` to extract the data from it.

!!! note
If you're familiar with MVC frameworks, a good way to think of this
concept is the inverse of a view: a `Page`
takes some kind of presentation (e.g. an HTML page or CSV
file) and converts it back to the underlying data that it is comprised of.

There are a few types of pages we generally encounter when scraping
sites. How we write and use our `Page` subclasses will depend upon which of these four roles the
page fulfills.

The two most common are what we'll call "listing" and "detail" pages.

Listing pages contain some kind of list of information, perhaps all of
the members of a given legislature. They'll often provide links to our
second type of page, which we'll call a "detail" page. A "detail"
page in our example would contain additional information on a single
legislator.

(TODO: revisit this section later) There are two other roles that a page
can play, we'll get into these in more detail in advanced topics.

One is what we'll call an 'auxillary detail' page, essentially a
subpage of a detail page that contains additional information we need to
collect. (An example would be if each detail page had a subpage listing
a legislator's committee assignments that we wanted to collect.) The
final role is what we call 'augmentation' pages, which provide data
with which we want to augment the entire data set. (An example would be
a separate page that is a photo directory of all legislators. We'll
need to scrape this and match the photos to the legislators we scraped
from the listing/detail pages.)

## Why don't page objects fetch themselves?

A big part of this is that we want to share some state among them for
rate limiting and other configuration yet to come. In theory this could
mean that each one is instantiated with a session parameter or similar,
but that'd be a bit more cumbersome. This also can make testing even
easier, as there's no need to mock HTTP requests/etc. as just passing a
mock object into the `Page` will suffice.
