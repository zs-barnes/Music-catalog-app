from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Product, User

engine = create_engine('sqlite:///musiccatalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()

User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

category1 = Category(user_id=1,name="Guitars")

session.add(category1)
session.commit()

product1 = Product(user_id=1, name="Gretsch Guitars Limited Edition Roots Series G9202 Honey Dipper Special Resonator Acoustic Guitar", 
                    description="The very sound and look of this fine Gretsch creation will make you want to free yourself from the damning confines of your office, your cubicle or whatever it is that enslaves you and hop the next train to anywhere with a smile on your face as big as the sky and a song in your heart.",
                     price="$549",category=category1)

session.add(product1)
session.commit()          

product2 = Product(user_id=1, name ="Fender American Professional Telecaster Maple Fingerboard Electric Guitar", 
                    description="Developed by vintage pickup master Tim Shaw, the brand-new V-Mod single-coil pickups are voiced specifically for each position, mixing alnico magnet types to produce powerful, nuanced tones with original Fender sonic DNA.",
                    price="$1,399.99", category=category1)

session.add(product2)
session.commit()

category2 = Category(user_id=1, name="Bass Guitars")

session.add(category2)
session.commit()          

product1 = Product(user_id=1, name="Fender Standard Precision Bass Guitar", 
                    description="The alder body, maple fretboard with jumbo frets, and split single-coil pickup deliver the fat tone that has driven rhythm sections for decades.",
                    price="$599.99",category=category2)

session.add(product1)
session.commit()



category3 = Category(user_id=1,name="Ukuleles, Mandolins, & Banjos")

session.add(category3)
session.commit()

product1 = Product(user_id=1, name="Diamond Head DU-150 Soprano Ukulele", 
                    description="Perfect for those who prefer the guitar-style geared tuners on their ukulele, the Diamond Head DU-150 Soprano Ukulele offers a gorgeous maple body that's stained mahogany brown, and its fingerboard and bridge are also constructed of maple but stained black.",
                    price="$33.95",category=category3)

session.add(product1)
session.commit()


category4 = Category(user_id=1, name="Amplifiers & Effects")

session.add(category4)
session.commit() 

product1 = Product(user_id=1, name="Fender Vintage Reissue '65 Twin Reverb 85W 2x12 Guitar Combo Amp", 
                    description="The Fender '65 Twin Reverb Amp is an authentic all-tube reproduction of the original classic!",
                    price="$1,449.99",category=category4)

session.add(product1)
session.commit()


category5 = Category(user_id=1, name="Drums & Percussion")

session.add(category5)
session.commit()

product1 = Product(user_id=1, name="Ludwig Supraphonic Snare Drum", 
                    description="The Ludwig Supraphonic Snare Drum features chrome metal shell construction that offers a bright, cutting, and crisp sound.",
                    price="$499.99",category=category5)

session.add(product1)
session.commit()



category6 = Category(user_id=1, name="Band & Orchestral Instruments")

session.add(category6)
session.commit()   

product1 = Product(user_id=1, name="Bach 180S37 Stradivarius Series Bb Trumpet", 
                    description="The Bach Stradivarius 180S37 Silver Professional Bb Trumpet offers the depth and color of sound, coupled with the even intonation and response a professional player needs.",
                    price="$2,829",category=category6)

session.add(product1)
session.commit()


category7 = Category(user_id=1, name="Keyboards & MIDI")

session.add(category7)
session.commit()

product1 = Product(user_id=1, name="Korg SV-1 73-Key Stage Vintage Piano Limited Edition Metallic Red", 
                    description="The Korg SV-173 Stage Vintage contains hip, in-demand, and soul-satisfying keyboard sounds collected together in a single instrument.",
                    price="$1,549.99",category=category7)

session.add(product1)
session.commit()


category8 = Category(user_id=1, name="Recording")

session.add(category8)
session.commit()    

product1 = Product(user_id=1, name="Universal Audio Apollo Twin MKII DUO Thunderbolt Audio Interface", 
                    description="The next generation Apollo Twin Series is a ground up redesign of the original delivering enhanced audio conversion with the tone, feel and flow of analog recording.",
                    price="$899.99",category=category8)

session.add(product1)
session.commit()


category9 = Category(user_id=1, name="DJ Gear")

session.add(category9)
session.commit()

product1 = Product(user_id=1, name="Behringer DDM4000 Pro Digital DJ Mixer", 
                    description="The Behringer DDM4000 is a state-of-the-art, 32-bit digital DJ mixer.",
                    price="$349.99",category=category9)

session.add(product1)
session.commit()

print "added categories & items!"