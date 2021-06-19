# Use this module to test functions & run arbitrary scripts
#within the context of this application.
# The block below must not be removed and must come first before any imports.
print("Initializing script runner...", end="")
######################################################################
import os                                                            #
import django                                                        #
                                                                     #
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mirapayments.settings")   #
django.setup()                                                       #
######################################################################
print("Ready!")


from djmoney.money import Money

amount = Money(100, 'NGN')

price = Money(200.025, 'USD')

print(price.round(2))


