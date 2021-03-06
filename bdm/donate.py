from decimal import Decimal

from zope.interface import implements

from epsilon.extime import Time

from axiom.item import Item
from axiom.attributes import text, point2decimal, timestamp, reference, boolean

from bdm.ibdm import IDonator, IDonation


class Donator(Item):
    implements(IDonator)

    steamID = text(allowNone=True, doc=u'64-bit SteamID')
    anonymous = boolean(allowNone=False, doc=u'Display the user publicly?')
    totalAmount = point2decimal(allowNone=False, default=Decimal('0'))

    @property
    def donations(self):
        return self.powerupsFor(IDonation)


    def getDonationAmount(self):
        return Decimal(sum(donation.amount for donation in self.donations))


    def addDonation(self, amount, paypalID):
        donation = Donation(store=self.store, amount=amount, paypalID=paypalID)
        donation.installOn(self)
        return donation


    def calculateTotal(self):
        """
        Calls L{getDonationAmount} and sets L{totalAmount} to the result.
        """
        self.totalAmount = self.getDonationAmount()



class Donation(Item):
    implements(IDonation)

    amount = point2decimal(allowNone=False, default=Decimal('0'))
    date = timestamp(defaultFactory=lambda: Time(), indexed=True)
    paypalID = text(allowNone=False)
    donator = reference()

    def installOn(self, donator):
        self.donator = donator
        donator.powerUp(self, IDonation)
        self.donator.calculateTotal()


    def deleteFromStore(self, deleteObject=True):
        """
        Recalculate total donation amount when donation is deleted
        """
        donator = self.donator
        super(Donation, self).deleteFromStore(deleteObject=deleteObject)
        donator.calculateTotal()



def donationToDict(donation):
    return {
        'donator': getattr(getattr(donation, 'donator', None), 'steamID', None),
        'amount': str(donation.amount),
        'date': donation.date.asPOSIXTimestamp()}


def donatorToDict(donator):
    return {
        'steamID': donator.steamID,
        'amount': str(donator.totalAmount)}
