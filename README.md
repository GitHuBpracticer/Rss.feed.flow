# Rss.feed.flow

personnal rss flux solution

## Prise en main rapide

1. Vérifie que les dépendances Python sont installées :
   ```bash
   pip install -r requirements.txt
   ```
2. Modifie les sources de flux dans `feeds_config.json` si tu veux ajouter, désactiver ou renommer un flux.
3. Génère les fichiers RSS :
   ```bash
   python rss_builder.py
   ```
4. Les flux XML seront créés dans le dossier racine du projet.
5. La page `index.html` sert de vitrine pour copier les liens vers ton lecteur RSS préféré (ReadYou, Feeder, Inoreader, etc.).

## Fichier de configuration

Le fichier `feeds_config.json` contient la liste des flux à générer.

Exemple :
```json
{
  "feeds": [
    {
      "name": "Permaculture",
      "enabled": true,
      "url": "https://permatheque.fr/",
      "description": "Flux Permaculture",
      "xml_filename": "permatheque.xml",
      "logo": "permatheque.jpg",
      "scraper": "scrape_permatheque",
      "max_items": 20
    }
  ]
}
```

### Que tu peux modifier facilement
- `enabled`: met `false` pour désactiver un flux sans le supprimer
- `url`: remplace la source du flux
- `xml_filename`: nom du fichier généré
- `logo`: nom de l'icône dans le dossier `icons/`
- `max_items`: limite le nombre d'articles exportés

## Lecteurs RSS supportés

Le script est conçu pour rester compatible avec :
- ReadYou
- Feeder
- Inoreader
- NetNewsWire
- Feedly
- autres lecteurs standards

## Fichiers générés

- `geo_histoire.xml`
- `permatheque.xml`
- `web3_airdrops.xml`
- `meteo_france.xml`
- `meteo_cote_dor.xml`
- `tech_ia.xml`
- `index.html`

## Logs

Le script enregistre des informations dans le dossier `logs/` et affiche aussi les messages dans le terminal.

Cela permet de vérifier rapidement :
- si un flux a bien été généré
- s'il y a eu une erreur sur une source
- combien d'articles ont été traités

## Astuce

Si tu veux ajouter un nouveau flux, il suffit de :
1. créer un scraper dans `rss_builder.py`
2. ajouter une entrée dans `feeds_config.json`
3. relancer `python rss_builder.py`

Cela évite de modifier le code principal à chaque ajout.
