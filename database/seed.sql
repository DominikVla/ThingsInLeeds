USE things_in_leeds;

INSERT INTO categories (name) VALUES
('Pub'), ('Cocktail Bar'), ('Museum'), ('Gallery'), ('Budget Hotel'),
('Boutique Hotel'), ('Street Food'), ('Live Music'), ('Club'), ('Restaurant'),
('Café'), ('Art'), ('History'), ('Family'), ('Shopping'), ('Nightlife');

INSERT INTO venues
(name, venue_type, description, neighbourhood, latitude, longitude, address, postcode, price_tier, website_url)
VALUES
('Royal Armouries Museum','attraction','National museum of arms and armour beside Leeds Dock','Leeds Dock',53.791614,-1.532050,'Armouries Drive','LS10 1LT',1,'https://royalarmouries.org/'),
('Leeds City Museum','attraction','Leeds history, natural world and local collections','City Centre',53.801825,-1.547707,'Millennium Square','LS2 8BH',1,'https://museumsandgalleries.leeds.gov.uk/'),
('Leeds Art Gallery','attraction','Historic and contemporary art collection','City Centre',53.800420,-1.548370,'The Headrow','LS1 3AA',1,'https://museumsandgalleries.leeds.gov.uk/'),
('Belgrave Music Hall','hospitality','Independent music venue, rooftop and street food','New Briggate',53.800790,-1.541020,'Cross Belgrave Street','LS2 8DD',2,'https://belgravemusichall.com/'),
('The Old Red Bus Station','hospitality','Community bar, arts and music space','South Bank',53.791220,-1.539470,'Vicar Lane','LS2 7NL',1,'https://www.theoldredbusstation.com/'),
('The Queens Hotel','accommodation','Historic grand hotel near Leeds railway station','City Centre',53.794472,-1.547643,'New Station Street','LS1 1PJ',3,'https://www.thequeensleeds.co.uk/'),
('ibis Leeds Centre','accommodation','Modern budget hotel close to the station','City Centre',53.796630,-1.548070,'Wade Lane','LS2 8NJ',2,'https://all.accor.com/');

-- Seed remaining Leeds venues deterministically (193 additional entries).
WITH RECURSIVE n AS (
  SELECT 1 AS i
  UNION ALL
  SELECT i + 1 FROM n WHERE i < 193
)
INSERT INTO venues
(name, venue_type, description, neighbourhood, latitude, longitude, address, postcode, price_tier, website_url)
SELECT CONCAT(
         CASE i % 5
           WHEN 0 THEN 'Headingley '
           WHEN 1 THEN 'Call Lane '
           WHEN 2 THEN 'Hyde Park '
           WHEN 3 THEN 'Northern Quarter '
           ELSE 'City Centre '
         END,
         CASE i % 3
           WHEN 0 THEN 'Local Venue '
           WHEN 1 THEN 'Leeds Social '
           ELSE 'Independent Spot '
         END,
         i),
       CASE i % 3
         WHEN 0 THEN 'hospitality'
         WHEN 1 THEN 'attraction'
         ELSE 'accommodation'
       END,
       'Leeds venue with local food, entertainment or visitor facilities',
       CASE i % 5
         WHEN 0 THEN 'Headingley'
         WHEN 1 THEN 'Call Lane'
         WHEN 2 THEN 'Hyde Park'
         WHEN 3 THEN 'Merrion Centre'
         ELSE 'City Centre'
       END,
       53.800000 + (i % 20) * 0.00080,
       -1.550000 + (i % 25) * 0.00055,
       CONCAT(i, ' Leeds Road'),
       CONCAT('LS', 1 + i % 18, ' ', 1 + i % 9, 'AA'),
       1 + i % 4,
       CONCAT('https://example.com/leeds/', i)
FROM n;

INSERT IGNORE INTO venue_categories (venue_id, category_id)
SELECT v.id,
       CASE MOD(v.id, 5)
         WHEN 0 THEN (SELECT id FROM categories WHERE name='Pub')
         WHEN 1 THEN (SELECT id FROM categories WHERE name='Cocktail Bar')
         WHEN 2 THEN (SELECT id FROM categories WHERE name='Museum')
         WHEN 3 THEN (SELECT id FROM categories WHERE name='Gallery')
         ELSE (SELECT id FROM categories WHERE name='Restaurant')
       END
FROM venues v;
