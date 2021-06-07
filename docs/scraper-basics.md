# A First Scraper

This guide contains quick examples of how you could scrape a small list
of employees of the fictional [Yoyodyne Propulsion
Systems](https://yoyodyne-propulsion.herokuapp.com/), a site developed
for demonstrating web scraping. This will give you an idea of what it
looks like to write a scraper using *spatula*.


## Scraping a List Page

It is fairly common for a scrape to begin on some sort of directory or
listing page.

We'll start by scraping the staff list on
<https://yoyodyne-propulsion.herokuapp.com/staff>

This page has a fairly simple HTML table with four columns:

``` html
<table id="employees">
  <thead>
    <tr>
      <th>First Name</th>
      <th>Last Name</th>
      <th>Position Name</th>
      <th>&nbsp;</th>
    </tr>
  </thead>
  <tbody>
  <tr>
    <td>John</td>
    <td>Barnett</td>
    <td>Scheduling</td>
    <td><a href="/staff/52">Details</a></td>
  </tr>
  <tr>
    <td>John</td>
    <td>Bigbooté</td>
    <td>Executive Vice President</td>
    <td><a href="/staff/2">Details</a></td>
  </tr>

  ...continues...
```

*spatula* provides a special interface for these cases. See below how
we process each matching link by deriving from a `HtmlListPage`
and providing a `selector` as well as a `process_item`  method.

Open a file named quickstart.py and add the following code:

``` python
# imports we'll use in this example
from spatula import (
    HtmlPage, HtmlListPage, CSS, XPath
)


class EmployeeList(HtmlListPage):
    source = "https://yoyodyne-propulsion.herokuapp.com/staff"

    # each row represents an employee
    selector = CSS("#employees tr")

    def process_item(self, item):
        # this function is called for each <tr> we get from the selector
        # we know there are 4 <tds>
        first, last, position, details = item.getchildren()
        return dict(
            first=first.text,
            last=last.text,
            position=position.text,
        )
```

One concept in spatula is that we typically write one class per type of
page we encounter. This class defines the logic to process the employee
list page. This class will turn each row on the page into a dictionary
with the 'first', 'last', and 'position' keys.

It can be tested from the command line like:

``` console
$ spatula test quickstart.EmployeeList
INFO:quickstart.EmployeeList:fetching https://yoyodyne-propulsion.herokuapp.com/staff
1: {'first': 'John', 'last': 'Barnett', 'position': 'Scheduling'}
2: {'first': 'John', 'last': 'Bigbooté', 'position': 'Executive Vice President'}
3: {'first': 'John', 'last': 'Camp', 'position': 'Human Resources'}
...
10: {'first': 'John', 'last': 'Fish', 'position': 'Marine R&D'}
```

The `spatula test` command lets us quickly see the output of the part of
the scraper we're working on.

You may notice that we're only grabbing the first page for now, we'll
come back in a bit to handle pagination.

## Scraping a Single Page

Employees have a few more details not included in the table on pages
like <https://yoyodyne-propulsion.herokuapp.com/staff/52>.

We're going to pull some data elements from the page that look like:

``` html
<h2 class="section">Employee Details for John Barnett</h2>
<div class="section">
  <dl>
    <dt>Position</dt>
    <dd id="position">Scheduling</dd>
    <dt>Marital Status</dt>
    <dd id="status">Married</dd>
    <dt>Number of Children</dt>
    <dd id="children">1</dd>
    <dt>Hired</dt>
    <dd id="hired">3/6/1963</dd>
  </dl>
</div>
```

To demonstrate extracting the details from this page, we'll write a
small class to handle individual employee pages.

Whereas before we used `HtmlListPage` and overrode `process_item`, this time
we'll subclass `HtmlPage`, and override the `process_page` function.

``` python
class EmployeeDetail(HtmlPage):
    def process_page(self):
        marital_status = CSS("#status").match_one(self.root)
        children = CSS("#children").match_one(self.root)
        hired = CSS("#hired").match_one(self.root)
        return dict(
            marital_status=marital_status.text,
            children=children.text,
            hired=hired.text,
        )
```

This will extract the elements from the page and return them in a dictionary.

It can be tested from the command line like:

``` console
$ spatula test quickstart.EmployeeDetail --source "https://yoyodyne-propulsion.herokuapp.com/staff/52"
INFO:quickstart.EmployeeDetail:fetching https://yoyodyne-propulsion.herokuapp.com/staff/52
{'children': '1', 'hired': '3/6/1963', 'marital_status': 'Married'}
```

One thing to note is that since we didn't define a single source attribute like we did in `EmployeeList`, we need to pass one on the command line with `--source`.
This lets you quickly try your scraper against multiple variants of a page as needed.

## Chaining Pages Together

Most moderately complex sites will require chaining data together from
multiple pages to get a complete object.

Let's revisit `EmployeeList` and have it return instances of `EmployeeDetail` 
to tell *spatula* that more work is needed:

``` python hl_lines="13 19 20"
class EmployeeList(HtmlListPage):
     # by providing this here, it can be omitted on the command line
     # useful in cases where the scraper is only meant for one page
     source = "https://yoyodyne-propulsion.herokuapp.com/staff"

     # each row represents an employee
     selector = CSS("#employees tbody tr")

     def process_item(self, item):
         # this function is called for each <tr> we get from the selector
         # we know there are 4 <tds>
         first, last, position, details = item.getchildren()
         return EmployeeDetail(
             dict(
                 first=first.text,
                 last=last.text,
                 position=position.text,
             ),
             source=XPath("./a/@href").match_one(details),
         )
```

And we can revisit `EmployeeDetail` to tell it to combine the data it collects with the data passed in from the parent page:

``` python hl_lines="10 11 12"
class EmployeeDetail(HtmlPage):
    def process_page(self):
        marital_status = CSS("#status").match_one(self.root)
        children = CSS("#children").match_one(self.root)
        hired = CSS("#hired").match_one(self.root)
        return dict(
            marital_status=marital_status.text,
            children=children.text,
            hired=hired.text,
            # self.input is the data passed in from the prior scrape,
            # in this case a dict we can expand here
            **self.input,
        )
```

Now a run looks like:

``` console
$ spatula test quickstart.EmployeeList
INFO:quickstart.EmployeeList:fetching https://yoyodyne-propulsion.herokuapp.com/staff
1: EmployeeDetail(input={'first': 'John', 'last': 'Barnett', 'position': 'Scheduling'} source=https://yoyodyne-propulsion.herokuapp.com/staff)
2: EmployeeDetail(input={'first': 'John', 'last': 'Bigbooté', 'position': 'Executive Vice President'} source=https:/yoyodyne-propulsion.herokuapp.com/staff/2)
...
10: EmployeeDetail(input={'first': 'John', 'last': 'Fish', 'position': 'Marine R&D'} source=https:/yoyodyne-propulsion.herokuapp.com/staff/20)
```

By default, `spatula test` just shows the result of the page you're
working on, but you can see that it is now returning page objects with
the data and a `source` set.

## Running a Scrape

Now that we're happy with our individual page scrapers, we can run the
full scrape and write the data to disk.

For this we use the `spatula scrape` command:

``` console
$ spatula scrape quickstart.EmployeeList
INFO:quickstart.EmployeeList:fetching https://yoyodyne-propulsion.herokuapp.com/staff
INFO:quickstart.EmployeeDetail:fetching https://yoyodyne-propulsion.herokuapp.com/staff/52
INFO:quickstart.EmployeeDetail:fetching https://yoyodyne-propulsion.herokuapp.com/staff/2
...
INFO:quickstart.EmployeeDetail:fetching https://yoyodyne-propulsion.herokuapp.com/staff/100
INFO:quickstart.EmployeeDetail:fetching https://yoyodyne-propulsion.herokuapp.com/staff/101
success: wrote 10 objects to _scrapes/2021-06-03/001
```

And now our scraped data is on disk, ready for you to use!

If you look at a data file you'll see that it has the full data for an
individual:

``` json
{
  "marital_status": "Single",
  "children": "0",
  "hired": "9/9/1963",
  "first": "John",
  "last": "Omar",
  "position": "Imports & Exports"
}
```

In [Next Steps](next-steps.md) we'll take a look at how to handle pagination, error handling, and validating scraped data.