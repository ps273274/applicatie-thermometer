voor de eerste keer opstarten, zet de website niet open door rechtsonderin op live te drukken 
Gebruik de terminal in visual studio code, je kan een nieuwe openen door helemaal bovenaan het scherm op terminal te klikken
1. Clonen
Begin met de website te clonen in visual studio, open source control linksbovenin je scherm onder het vergrootglas dan heb je bij repositories als het goed is 3
puntjes en als je daarop klikt heb je een knop clone dan zou deze je naar de balk bovenin je scherm moeten sturen en daarin plak je de link hieronder: 
git clone: https://github.com/ps273274/applicatie-thermometer

3. naar de juiste map gaan
Ga dan in de terminal in visual studio met cd naar de map waarin je het bestand hebt opgeslagen in deze map zou cd /Thermometerv3/dockerfile/

4. starten
Als dit gedaan is kan je het bestand starten door docker compose up -d in de terminal te typen. Misschien moet je dan wel docker desktop open hebben staan maar dat
weet ik niet zeker dan ga je naar de website door deze link te gebruiken: http://localhost:3001

5. sluiten
Als je klaar bent dan kan je hem weer sluiten door in de terminal op visual studio docker compose down te typen. Zo slaat docker de wijzigingen ook niet verder op



voor vaker openen:
1. Kijk in github of er een nieuwe versie in staat.
2. Open een nieuwe terminal.
3. Ga in de docker folder.
4. Docker compose up -d om te starten (misschien docker desktop ook open zetten).
5. klaar met programmeren, push het bestand naar github zodat ze volgende deze met wijzigingen kan pakken. (Ga niet met zijn 2en tegelijk in dezelfde file dingen
aanpassen, dan werkt de push en pull niet.
6.Sluit docker af met git compose down.
