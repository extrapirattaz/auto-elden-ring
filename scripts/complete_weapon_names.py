"""Maintain editorial Czech names and supplemental DLC translations.

Official imported strings take precedence. Editorial strings are explicitly
identified in SOURCES.md; this is not an official Czech game localization.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CZECH = """
dagger|Dýka|Černý nůž|Odrazová dýka|Misericordia|Reduvia|Křišťálový nůž|Srp oslavence|Kris třpytivého kamene|Štíří žihadlo|Velký nůž|Wakizaši|Cinquedea|Slonovinový srp|Zkrvavená dýka|Dýka ze stromové oceli|Čepel přivolání|Levoruční dýka|Krátký meč ohnivého rytíře
straight_sword|Dlouhý meč|Krátký meč|Široký meč|Přímý meč přísežného vojáka|Zvětralý přímý meč|Zdobený přímý meč|Zlatý epitaf|Meč šifry|Meč noci a plamene|Křišťálový meč|Meč carijského rytíře|Meč svaté Triny|Meč Miquellova rytíře|Meč v holi|Eochaidovy regálie|Štíhlý meč šlechtice|Pařát válečného jestřába|Lazulitový meč|Zkažený křišťálový meč|Sametový meč svaté Triny|Meč v kamenné pochvě|Meč světla|Meč temnoty
curved_sword|Tekoucí meč Noxů|Falchion|Zahnutý meč zvířecího muže|Šotel|Šamšír|Zahnutý meč bandity|Magmatická čepel|Tekoucí zahnutý meč|Astelovo křídlo|Zahnutý meč mrchožrouta|Šotel zatmění|Zahnutý meč hadího boha|Čepel kudlanky|Scimitar|Grossmesser|Meč ducha|Falx|Tančící čepel Ranahu|Meč rohatého válečníka
greatsword|Nerozlučný meč|Bastard|Rozvětvený velký meč|Železný velký meč|Velký meč přísežného vojáka|Velký meč rytíře|Flamberge|Ordovisův velký meč|Meč alabastrového pána|Velký meč vyhnaného rytíře|Velký meč temného měsíce|Meč posvátné relikvie|Helphenova věž|Rouhavá čepel|Popravčí meč rodu Marais|Milosův meč|Velký meč Zlatého řádu|Claymore|Velký meč chrliče|Pohrabáč smrti|Černá čepel chrliče|Velký meč zatracení|Ještěří velký meč|Velký meč samoty|Leontielův velký meč
katana|Meč hvězdných čar|Učigatana|Nagakiba|Maleniina ruka|Čepel meteoritové rudy|Řeky krve|Měsíční závoj|Čepel dračích šupin|Čepel hadí kosti|Meč noci
thrusting_sword|Carijský čarodějný meč|Estoc|Meč rytíře čisté hniloby|Rapír|Rogierův rapír|Rapír mravenčího trnu|Zmrzlá jehla|Estoc šlechtice
heavy_thrusting_sword|Mečové kopí|Krvavá šroubovice|Sešívač boží kůže|Velký kord|Skalní čepel dračího krále|Queelignův velký meč
colossal_sword|Velký meč|Velký meč strážního psa|Malikethova černá čepel|Trollův zlatý meč|Zweihänder|Velký meč zhoubce hvězd|Královský velký meč|Velký meč bohovraha|Velký meč ruin|Velký meč roubovaných čepelí|Meč trollího rytíře|Prastarý meteoritový velký meč|Velký meč ohnivého rytíře|Radahnův velký meč (pán)|Moonrithyllův rytířský meč|Radahnův velký meč (světlo)
curved_greatsword|Velký meč onyxového pána|Srážeč jezdců|Tesák krvavého slídiče|Šupinový meč magmatického draka|Zamorský zahnutý meč|Sekáček prokletých|Mnichova plamenná čepel|Sekáček zvířecího muže|Morgottův prokletý meč|Freyjin velký meč|Velký meč rohatého válečníka|Těžký scimitar
greataxe|Sekáček hniloby|Velká sekera|Velký sekáček lovce prokletých|Sekera půlměsíce|Godrickova sekera|Sekera s dlouhou násadou|Rezavá kotva|Katova velká sekera|Okřídlený velký roh|Řeznický nůž|Velká sekera chrliče|Černá sekera chrliče|Dlouhá sekera rytíře smrti|Bonnyský řeznický nůž
twinblade|Dvojčepel|Stahovač boží kůže|Dvojité rytířské meče|Eleonořina dvojčepel|Dvojčepel chrliče|Černé čepele chrliče|Euporia|Dvojčepel z černé oceli
hammer|Palcát|Kyj|Zahnutý kyj|Válečný krumpáč|Jitřenka|Varrého kytice|Ostnatý kyj|Kladivo|Mnichův plamenný palcát|Roh vyslance|Žezlo Vševědoucího|Tekoucí kladivo Noxů|Prstenový prst|Kamenný kyj|Maričino kladivo|Květokamenná palička
great_hammer|Velký kyj|Kladivo velkého rohu|Bojové kladivo|Velký palcát|Zahnutý velký kyj|Lebka oslavence|Krumpáč|Velké kladivo zvířecího drápu|Dlouhý roh vyslance|Lebkový svícen|Velké hvězdy|Cihlové kladivo|Žezlo požírače|Zkažené bojové kladivo|Velké kladivo kovářského písma|Velké kladivo z černé oceli
colossal_weapon|Kovadlinové kladivo|Paže krvavého démona|Prelátova pekelná berla|Hůl strážního psa|Obří kyj|Velký roh vyslance|Duelantova velká sekera|Godfreyho sekera|Velký dračí dráp|Hůl avatara|Čelist hvězdné bestie|Ghizovo kolo|Drtič obrů|Golemova halapartna|Trollí kladivo|Zkažená hůl|Zkažená velká sekera|Devoniino kladivo|Květ stínové slunečnice|Zírající prst
flail|Cep nočního jezdce|Cep|Rodinné hlavy|Bastardovy hvězdy|Řetězový cep|Hadí cep|Cep Zlatého řádu
axe|Bojová sekera|Rozvětvená sekerka|Ruční sekera|Sekera z čelisti|Železný sekáček|Čepel vlnění|Sekáček oslavence|Ledová sekerka|Sekera z vysočiny|Obětní sekera|Rosusova sekera|Sekera bouřného jestřába|Sekera kovářského písma|Dvojité sekery rytíře smrti|Sekera Messmerova vojáka|Sekerka rozeklaného jazyka|Zkřivená sekera
spear|Krátké kopí|Kopí|Křišťálové kopí|Harpuna hliněného muže|Kopí čisté hniloby|Partyzána|Žeberní hrábě oslavence|Píka|Pochodňové kopí|Gransaxův blesk|Křížová naginata|Kopí rituálu smrti|Inkvizitorův svícen|Ostnaté kopí|Železné kopí|Zkažené křišťálové kopí|Kopí kovářského písma|Rychlé kopí|Vidlice krvavého démona
great_spear|Posvátné kopí krvavého démona|Mohgwynovo posvátné kopí|Siluriin strom|Lovec hadů|Vykeovo válečné kopí|Jezdecké kopí|Stromové kopí|Kopí Napichovače|Kopí Messmerova vojáka|Ostnaté žezlové kopí
halberd|Halapartna|Kosa škůdce|Lucernské kladivo|Halapartna vyhnaného rytíře|Velitelova standarta|Kosa nočního jezdce|Halapartna vlnícího se půlměsíce|Pila prosté milice|Zlatá halapartna|Kosa|Lorettin válečný srp|Strážcův mečokopí|Šotel prosté milice|Dračí halapartna|Halapartna chrliče|Černá halapartna chrliče|Kosa ducha|Tyčová čepel poupěte
reaper|Kosa|Hrobová kosa|Kosa svatozáře|Okřídlená kosa|Obsidiánová čepel
whip|Bič|Trnitý bič|Svícen magmatického biče|Hoslowův okvětní bič|Obrův rudý cop|Urumi|Zubatý bič
fist|Caestus|Ostnatý caestus|Roubovaný drak|Železná koule|Hvězdná pěst|Katar|Přilnavá kost|Veteránova protéza|Šifrová pata|Thiollierova skrytá jehla|Pata|Jedovatá ruka|Šílená ruka|Golemova pěst
small_shield|Štít noci|Pěstní štítek|Štít parfuméra|Štít hadího muže|Vratký štít|Pranýřový štít|Kulatý štít rudého trnu|Dřevěný štít písma|Nýtovaný dřevěný štít|Modrobílý dřevěný štít|Štít trhliny|Železný kulatý štít|Pozlacený železný štít|Štít ledového erbu|Doutnající štít|Štít spirálového rohu|Stočený štít|Štít kovářského písma|Štít provinilých
claw|Hákové drápy|Jedovatý tesák|Drápy krvavého slídiče|Dravčí pařáty|Drápy noci
torch|Pochodeň|Pochodeň s ocelovým drátem|Pochodeň svaté Triny|Pochodeň přízračného plamene|Pochodeň odpuzující bestie|Strážní pochodeň|Nanayina pochodeň|Tvář nářku
medium_shield|Nádobový štít zvířecího muže|Mandlový štít|Poškozený kožený štít|Poškozený dřevěný štít|Štít vyhnaného rytíře|Štít albinauriků|Štít sluneční říše|Stříbrný zrcadlový štít|Kulatý štít|Mandlový štít štíra|Mandlový štít dvojice ptáků|Modrozlatý mandlový štít|Mosazný štít|Velký želví krunýř|Štít carijského rytíře|Velký kožený štít|Dřevěný štít s erbem koně|Dřevěný štít svícného stromu|Dřevěný štít s erbem plamene|Dřevěný štít s erbem jestřába|Štít s erbem bestie|Štít s rudým erbem|Štít s modrým erbem|Štít s erbem zatmění|Štít obráceného jestřába|Trojúhelníkový štít|Černý kožený štít|Štít Messmerova vojáka|Štít s erbem vlka|Štít s erbem hada|Štít zlatého lva|Stříbrný rýhovaný štít
greatshield|Dračí věžový štít|Vznešený velký štít|Rohový štít Tyglíku|Štít dračího drápu|Trnitý velký štít|Velký štít Zlatého stromu|Štít zlatého zvířecího erbu|Medúzí štít|Kamenný štít otisku prstu|Štít ikony|Jednooký štít|Štít tváře|Ostnatý palisádový štít|Věžový štít panství|Věžový štít zkřížených stromů|Věžový štít obráceného jestřába|Mravenčí lebka|Velký štít rudé hřívy|Velký štít zatmění|Velký štít kukačky|Zlatý velký štít|Pozlacený velký štít|Velký štít Svatého stromu|Dřevěný velký štít|Štít přísežného vojáka|Velký štít z černé oceli|Měděnkový velký štít
glintstone_staff|Hůl třpytivého kamene|Křišťálová hůl|Gelmirská hůl třpytivého kamene|Hůl královny pololidí|Carijské královské žezlo|Hůl kopáče|Hůl astrologa|Carijská hůl třpytivé čepele|Hůl prince smrti|Hůl albinauriků|Akademická hůl třpytivého kamene|Carijská hůl třpytivého kamene|Azurova hůl|Lusatova hůl|Meteoritová hůl|Hůl provinilých|Zkažená křišťálová hůl|Hůl ztráty|Hůl Velkého záhrobí|Mateřská hůl
sacred_seal|Prstová pečeť|Pečeť bohovraha|Obří pečeť|Pečeť štěrkového kamene|Pečeť drápů|Pečeť Zlatého řádu|Pečeť Zlatého stromu|Pečeť dračího přijímání|Pečeť šíleného plamene|Pečeť Suchého listu|Pečeť ohnivého rytíře|Pečeť spirálového stromu
light_bow|Krátký luk|Krátký luk znetvořených|Krátký luk rudé větve|Harfový luk|Kompozitní luk|Kostěný luk
bow|Dlouhý luk|Luk albinauriků|Rohový luk|Luk Zlatého stromu|Hadí luk|Kladkový luk|Černý luk|Ansbachův dlouhý luk
greatbow|Lví velký luk|Golemův velký luk|Velký luk Zlatého stromu|Velký luk|Igonův velký luk
crossbow|Vojákova kuše|Lehká kuše|Těžká kuše|Kladková kuše|Kuše úplňku|Arbaleta|Crepusova kuše černého klíče|Opakovací kuše|Rozptylová kuše
ballista|Ruční balista|Nádobové dělo|Rabbathovo dělo
hand_to_hand|Umění Suchého listu|Daneova práce nohou
perfume_bottle|Flakón ohnivých jisker|Flakón mrazivého parfému|Flakón šíleného plamene|Flakón bleskového parfému|Flakón smrtícího jedu
thrusting_shield|Soubojový štít|Carijský bodný štít|Rituální bodný štít
throwing_blade|Dýka kovářského písma
backhand_blade|Obrácená čepel|Kruh kovářského písma|Kruh prokleté čepele|Meč obrácené čepele
great_katana|Velká katana|Velká katana lovce draků|Rakshasova velká katana|Rákosová velká katana
light_greatsword|Milady|Ledin meč|Rellaniny dvojité čepele|Idův meč
beast_claw|Zvířecí dráp|Dráp rudého medvěda
"""

# Supplemental names follow the canonical missing-name order below. The game
# database's English identifiers stay stable regardless of display language.
DLC = """
Main-gauche|Main-gauche|Linkhanddolch|Mano izquierda
Fire Knight's Shortsword|Épée courte de chevalier de feu|Kurzschwert des Feuerritters|Espada corta de caballero de fuego
Velvet Sword of St. Trina|Épée de velours de sainte Trina|Samtschwert der heiligen Trina|Espada de terciopelo de santa Trina
Stone-Sheathed Sword|Épée au fourreau de pierre|Schwert in Steinscheide|Espada con vaina de piedra
Sword of Light|Épée de lumière|Schwert des Lichts|Espada de luz
Sword of Darkness|Épée des ténèbres|Schwert der Dunkelheit|Espada de oscuridad
Spirit Sword|Épée spirituelle|Geisterschwert|Espada espiritual
Falx|Falx|Falx|Falx
Dancing Blade of Ranah|Lame dansante de Ranah|Tanzende Klinge von Ranah|Hoja danzante de Ranah
Horned Warrior's Sword|Épée de guerrier cornu|Schwert des Hornkriegers|Espada de guerrero cornudo
Greatsword of Damnation|Espadon de damnation|Großschwert der Verdammnis|Espadón de condenación
Lizard Greatsword|Espadon lézard|Echsengroßschwert|Espadón de lagarto
Greatsword of Solitude|Espadon de solitude|Großschwert der Einsamkeit|Espadón de soledad
Leontiel's Greatsword|Espadon de Leontiel|Leontiels Großschwert|Espadón de Leontiel
Star-Lined Sword|Épée constellée|Sternenlinienschwert|Espada estrellada
Sword of Night|Épée de la nuit|Schwert der Nacht|Espada de la noche
Carian Sorcery Sword|Épée de sorcellerie carienne|Carianisches Zauberschwert|Espada de hechicería cariana
Sword Lance|Lance-épée|Schwertlanze|Lanza espada
Queelign's Greatsword|Espadon de Queelign|Queeligns Großschwert|Espadón de Queelign
Ancient Meteoric Ore Greatsword|Espadon de minerai météorique ancien|Uraltes Meteoritenerz-Großschwert|Espadón de mineral meteórico antiguo
Fire Knight's Greatsword|Espadon de chevalier de feu|Großschwert des Feuerritters|Espadón de caballero de fuego
Greatsword of Radahn (Lord)|Espadon de Radahn (seigneur)|Radahns Großschwert (Fürst)|Espadón de Radahn (señor)
Moonrithyll's Knight Sword|Épée de chevalier de Moonrithyll|Moonrithylls Ritterschwert|Espada de caballero de Moonrithyll
Greatsword of Radahn (Light)|Espadon de Radahn (lumière)|Radahns Großschwert (Licht)|Espadón de Radahn (luz)
Freyja's Greatsword|Espadon de Freyja|Freyjas Großschwert|Espadón de Freyja
Horned Warrior's Greatsword|Espadon de guerrier cornu|Großschwert des Hornkriegers|Espadón de guerrero cornudo
Hefty Scimitar|Cimeterre lourd|Schwerer Krummsäbel|Cimitarra pesada
Putrescence Cleaver|Fendoir de putrescence|Verwesungsspalter|Cuchilla de putrefacción
Death Knight's Longhaft Axe|Hache à long manche de chevalier de la mort|Langstielaxt des Todesritters|Hacha de mango largo de caballero de la muerte
Bonny Butchering Knife|Couteau de boucher de Bonny|Bonnys Schlachtmesser|Cuchillo de carnicero de Bonny
Euporia|Euporia|Euporia|Euporia
Black Steel Twinblade|Lame double en acier noir|Zwillingsklinge aus schwarzem Stahl|Hoja doble de acero negro
Flowerstone Gavel|Maillet de pierre florale|Blumensteinhammer|Mazo de piedra floral
Smithscript Greathammer|Grand marteau gravé|Schmiedeschrift-Großhammer|Gran martillo con inscripciones
Black Steel Greathammer|Grand marteau en acier noir|Großhammer aus schwarzem Stahl|Gran martillo de acero negro
Anvil Hammer|Marteau-enclume|Ambosshammer|Martillo yunque
Bloodfiend's Arm|Bras de démon sanguinaire|Arm des Blutdämons|Brazo de demonio sangriento
Devonia's Hammer|Marteau de Devonia|Devonias Hammer|Martillo de Devonia
Shadow Sunflower Blossom|Fleur de tournesol de l'ombre|Blüte der Schattensonnenblume|Flor de girasol de las sombras
Gazing Finger|Doigt scrutateur|Starrender Finger|Dedo observador
Serpent Flail|Fléau serpent|Schlangenflegel|Mayal serpiente
Golden Order Flail|Fléau de l'Ordre d'or|Flegel der Goldenen Ordnung|Mayal de la Orden Dorada
Smithscript Axe|Hache gravée|Schmiedeschrift-Axt|Hacha con inscripciones
Death Knight's Twin Axes|Haches jumelles de chevalier de la mort|Zwillingsäxte des Todesritters|Hachas gemelas de caballero de la muerte
Messmer Soldier's Axe|Hache de soldat de Messmer|Axt des Messmer-Soldaten|Hacha de soldado de Messmer
Forked-Tongue Hatchet|Hachette à langue fourchue|Spaltzungenbeil|Hachuela de lengua bífida
Smithscript Spear|Lance gravée|Schmiedeschrift-Speer|Lanza con inscripciones
Swift Spear|Lance rapide|Schnellspeer|Lanza veloz
Bloodfiend's Fork|Fourche de démon sanguinaire|Gabel des Blutdämons|Horca de demonio sangriento
Bloodfiend's Sacred Spear|Lance sacrée de démon sanguinaire|Heiliger Speer des Blutdämons|Lanza sagrada de demonio sangriento
Spear of the Impaler|Lance de l'Empaleur|Speer des Pfählers|Lanza del Empalador
Messmer Soldier's Spear|Lance de soldat de Messmer|Speer des Messmer-Soldaten|Lanza de soldado de Messmer
Barbed Staff-Spear|Lance-bâton barbelée|Stacheliger Stabspeer|Lanza bastón espinosa
Spirit Glaive|Glaive spirituel|Geisterglefe|Guja espiritual
Poleblade of the Bud|Lame du bourgeon|Stangenklinge der Knospe|Hoja de asta del brote
Obsidian Lamina|Lame d'obsidienne|Obsidianklinge|Lámina de obsidiana
Tooth Whip|Fouet à dents|Zahnpeitsche|Látigo de dientes
Thiollier's Hidden Needle|Aiguille cachée de Thiollier|Thiolliers verborgene Nadel|Aguja oculta de Thiollier
Pata|Pata|Pata|Pata
Poisoned Hand|Main empoisonnée|Vergiftete Hand|Mano envenenada
Madding Hand|Main de démence|Wahnsinnshand|Mano de locura
Golem Fist|Poing de golem|Golemfaust|Puño de gólem
Shield of Night|Bouclier de la nuit|Schild der Nacht|Escudo de la noche
Smithscript Shield|Bouclier gravé|Schmiedeschrift-Schild|Escudo con inscripciones
Claws of Night|Griffes de la nuit|Klauen der Nacht|Garras de la noche
Nanaya's Torch|Torche de Nanaya|Nanayas Fackel|Antorcha de Nanaya
Lamenting Visage|Visage lamentable|Klagendes Antlitz|Rostro de lamento
Messmer Soldier Shield|Bouclier de soldat de Messmer|Schild des Messmer-Soldaten|Escudo de soldado de Messmer
Wolf Crest Shield|Bouclier au blason du loup|Wolfsschild|Escudo con blasón de lobo
Serpent Crest Shield|Bouclier au blason du serpent|Schlangenwappenschild|Escudo con blasón de serpiente
Golden Lion Shield|Bouclier du lion doré|Goldener Löwenschild|Escudo del león dorado
Silver Grooved Shield|Bouclier argenté rainuré|Gerillter Silberschild|Escudo de plata acanalada
Black Steel Greatshield|Grand bouclier en acier noir|Großschild aus schwarzem Stahl|Gran escudo de acero negro
Verdigris Greatshield|Grand bouclier de vert-de-gris|Grünspangroßschild|Gran escudo de verdín
Staff of the Great Beyond|Bâton de l'au-delà|Stab des großen Jenseits|Bastón del Gran Más Allá
Maternal Staff|Bâton maternel|Mütterlicher Stab|Bastón maternal
Dryleaf Seal|Sceau de Feuille-morte|Trockenblatt-Siegel|Sello de Hoja Seca
Fire Knight's Seal|Sceau de chevalier de feu|Siegel des Feuerritters|Sello de caballero de fuego
Spiraltree Seal|Sceau de l'arbre spiralé|Spiralbaum-Siegel|Sello del árbol espiral
Bone Bow|Arc en os|Knochenbogen|Arco de hueso
Ansbach's Longbow|Arc long d'Ansbach|Ansbachs Langbogen|Arco largo de Ansbach
Igon's Greatbow|Grand arc d'Igon|Igons Großbogen|Gran arco de Igon
Repeating Crossbow|Arbalète à répétition|Repetierarmbrust|Ballesta de repetición
Spread Crossbow|Arbalète à dispersion|Streuarmbrust|Ballesta de dispersión
Rabbath's Cannon|Canon de Rabbath|Rabbaths Kanone|Cañón de Rabbath
Dryleaf Arts|Arts de Feuille-morte|Trockenblatt-Künste|Artes de Hoja Seca
Dane's Footwork|Jeu de jambes de Dane|Danes Beinarbeit|Juego de piernas de Dane
Firespark Perfume Bottle|Flacon de parfum étincelle de feu|Feuerfunken-Parfümflasche|Frasco de perfume de chispas de fuego
Chilling Perfume Bottle|Flacon de parfum givrant|Frost-Parfümflasche|Frasco de perfume helador
Frenzyflame Perfume Bottle|Flacon de parfum de flamme exaltée|Rasende-Flamme-Parfümflasche|Frasco de perfume de llama frenética
Lightning Perfume Bottle|Flacon de parfum de foudre|Blitz-Parfümflasche|Frasco de perfume de rayo
Deadly Poison Perfume Bottle|Flacon de parfum mortel|Tödliches-Gift-Parfümflasche|Frasco de perfume de veneno mortal
Dueling Shield|Bouclier de duel|Duellschild|Escudo de duelo
Carian Thrusting Shield|Bouclier d'estoc carien|Carianischer Stoßschild|Escudo de embestida cariano
Ritual Thrusting Shield|Bouclier d'estoc rituel|Ritueller Stoßschild|Escudo de embestida ritual
Smithscript Dagger|Dague gravée|Schmiedeschrift-Dolch|Daga con inscripciones
Backhand Blade|Lame inversée|Rückhandklinge|Hoja de revés
Smithscript Cirque|Cirque gravé|Schmiedeschrift-Ringklinge|Círculo con inscripciones
Curseblade's Cirque|Cirque de lame maudite|Ringklinge der Fluchklinge|Círculo de hoja maldita
Reverse-Bladed Sword|Épée à lame inversée|Umkehrklingenschwert|Espada de hoja invertida
Great Katana|Grand katana|Großkatana|Gran katana
Dragon-Hunter's Great Katana|Grand katana de chasseur de dragons|Großkatana des Drachenjägers|Gran katana de cazador de dragones
Rakshasa's Great Katana|Grand katana de Rakshasa|Rakshasas Großkatana|Gran katana de Rakshasa
Reed Great Katana|Grand katana des roseaux|Schilf-Großkatana|Gran katana de junco
Milady|Milady|Milady|Milady
Leda's Sword|Épée de Leda|Ledas Schwert|Espada de Leda
Rellana's Twin Blades|Lames jumelles de Rellana|Rellanas Zwillingsklingen|Hojas gemelas de Rellana
Idus Sword|Épée d'Idus|Idus-Schwert|Espada de Idus
Beast Claw|Griffe bestiale|Bestienklaue|Garra de bestia
Red Bear's Claw|Griffe de l'ours rouge|Klaue des roten Bären|Garra de oso rojo
"""
JAPANESE_NEW = {
    "Leontiel's Greatsword": "レオンティエルの大剣",
    "Silver Grooved Shield": "銀の溝付き盾",
    "Golden Order Flail": "黄金律のフレイル",
    "Forked-Tongue Hatchet": "二股舌の手斧",
    "Spiraltree Seal": "螺旋樹の聖印",
    "Ritual Thrusting Shield": "儀式の刺突盾",
    "Reverse-Bladed Sword": "逆刃の剣",
    "Reed Great Katana": "葦の大刀",
    "Idus Sword": "イダスの剣",
    "Hefty Scimitar": "重いシミター",
}


def main():
    database = json.loads((ROOT / "elden_ring_costs.json").read_text(encoding="utf-8"))
    path = ROOT / "assets/weapon_names.json"
    names = json.loads(path.read_text(encoding="utf-8"))
    for line in CZECH.strip().splitlines():
        category, *translations = line.split("|")
        canonical = list(database["weapons_by_category"][category])
        if len(canonical) != len(translations):
            raise ValueError(f"Czech category length mismatch: {category}")
        names["cs"].update(zip(canonical, translations))
    for line in DLC.strip().splitlines():
        name, *translations = line.split("|")
        for locale, translation in zip(("fr", "de", "es"), translations):
            names[locale].setdefault(name, translation)
    names["ja"].update({k: v for k, v in JAPANESE_NEW.items() if k not in names["ja"]})
    for entries in database["weapons_by_category"].values():
        for name in entries:
            names["en"].setdefault(name, name)
    missing = {
        locale: [
            n
            for entries in database["weapons_by_category"].values()
            for n in entries
            if n not in table
        ]
        for locale, table in names.items()
    }
    if any(missing.values()):
        raise ValueError(missing)
    path.write_text(json.dumps(names, ensure_ascii=False, indent=2), encoding="utf-8")
    print({locale: len(table) for locale, table in names.items()})


if __name__ == "__main__":
    main()
