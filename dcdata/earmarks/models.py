from django.contrib.localflavor.us.models import USStateField
from django.db import models
from dcdata.models import Import


bill_choices = 
    (('a', 'Ag-Rural Development-FDA'),
    ('c', 'Commerce-Justice-Science'),
    ('d', 'Defense'),
    ('s', 'Defense Supplemental'),
    ('j', 'Disaster Aid'),
    ('e', 'Entergy & Water'),
    ('f', 'Financial Services'),
    ('h', 'Homeland Security'),
    ('i', 'Interior'),
    ('l', 'Labor-HHS-Education'),
    ('g', 'Legislative Branch'),
    ('m', 'Military Construction'),
    ('o', 'State-Foreign Ops'),
    ('t', 'Transportation-Housing and Urban Development'))

# mapping from bill names as they appear in TCS files to model abbreviations
bill_raw = dict([
    ("Ag-Rural Development-FDA", 'a'),
    ("Commerce-Justice-Science", 'c'),
    ("Commerce, Justice & Science", 'c'),
    ("Defense", 'd'),
    ("Defense Supplemental", 's'),
    ("Disaster Aid", 'j'),
    ("Energy & Water", 'e'),
    ("Energy and Water", 'e'),
    ("Financial Services", 'f'),
    ("Homeland Security", 'h'),
    ("Interior", 'i'),
    ("Labor-HHS-Education", 'l'),
    ("Legislative Branch", 'g'),
    ("Military Construction", 'm'),
    ("State-Foreign Ops", 'o'),
    ("Transportation-Housing and Urban Development", 't'),
    ("Transportation and Housing & Urban Development", 't')])


presidential_choices =
    (('p', "President - solo"),
    ('u', "President - solo & und.")),
    ('m', "President - with member(s)"),
    ('j', "Judiciary"))

presidential_raw = dict([
    ("President-Solo", 'p'),
    ("President - solo", 'p'),
    ("President-Solo & Und.", 'u'), # don't know what this means --epg
    ("President and Member(s)", 'm'),
    ("President with member(s)", 'm'),
    ("President - with member(s)", 'm'),
    ("Judiciary", 'j')])


undisclosed_choices =
    (('u', "Undisclosed"),
    ('p', "Undisclosed (President)"),
    ('o', "O & M-Disclosed"),
    ('m', "O & M-Undisclosed"))

undisclosed_raw = dict([
    ("Undisclosed", 'u'),
    ("Undisclosed (President)", 'p'),
    ("O & M-Disclosed", 'o'), # don't know what this means --epg
    ("O & M-Undisclosed", 'm'), # don't know what this means --epg
])


chamber_choices =
    (('h', "House"),
    ('s', "Senate"))


party_choices =
    (('r', "Republican"),
    ('d', "Democrat"),
    ('i', "Independent"))


class Earmark(models.Model):
    import_reference = models.ForeignKey(Import)
    
    fiscal_year = models.IntegerField()
    
    budget_amount = models.DecimalField(default=0, max_digits=15, decimal_places=2)
    house_amount = models.DecimalField(default=0, max_digits=15, decimal_places=2)
    senate_amount = models.DecimalField(default=0, max_digits=15, decimal_places=2)
    final_amount = models.DecimalField(default=0, max_digits=15, decimal_places=2)
    
    # should we call it 'location' instead?
    city = models.CharField(max_length=128, blank=True)
    state = USStateField(blank=True)
    
    bill = model.CharField(max_length=64, choices=bill_choices, blank=False)
    bill_section = model.CharField(max_length=255, blank=True)
    bill_subsection = model.CharField(max_length=255, blank=True)
    
    # possible that we'll need to increase the length if we see long values
    description = model.CharField(max_length=255, blank=True)
    notes = model.CharField(max_length=255, blank=True)
    
    presidential = model.CharField(max_length=1, choices=presidential_choices, blank=True)
    undisclosed = model.CharField(max_length=1, choices=undisclosed_choices, blank=True)
    
    raw_recipient = model.CharField(max_length=128, blank=True)
    standardized_recipient = model.CharField(max_length=128, blank=True)


class Member(models.Model):
    earmark = models.ForeignKey(Earmark)
    
    raw_name = model.CharField(max_length=64)
    crp_id = models.CharField(max_length=128, blank=True)
    standardized_name = models.CharField(max_length=128, blank=True)
    
    chamber = model.CharField(max_length=1, choices=chamber_choices)    
    party = model.CharField(max_length=1, choices=party_choices)
    state = USStateField(blank=True)

