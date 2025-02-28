INSERT INTO balance_sheet ("category", "2021", "Jan 22", "Feb 22", "Mär 22", "Apr 22", "Mai 22", "Jun 22", "Jul 22", "Aug 22", "Sep 22", "Okt 22", "Nov 22", "Dez 22", "Abw. VJ") VALUES 
('Anlagevermögen', 643194.0, 645084.0, 645524.0, 645524.0, 674336.0, 676683.0, 711081.0, 711081.0, 703099.0, 695286.0, 693127.0, 699215.0, 694032.0, 0.079),
('Immaterielle Vermögensgegenstände', 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, NULL),
('Grundstücke und Gebäude', 130136.0, 130136.0, 130136.0, 130136.0, 130136.0, 130136.0, 130136.0, 130136.0, 130060.0, 129985.0, 129909.0, 129834.0, 129758.0, -0.003),
('Betriebs- und Geschäftsausstattung', 487901.0, 489791.0, 490231.0, 490231.0, 519043.0, 521390.0, 555788.0, 555788.0, 547882.0, 540144.0, 538060.0, 544224.0, 539116.0, 0.105),
('geleistete Anzahlungen und Anlagen im Bau', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

INSERT INTO revenue_trends ("KUNDEN", "2017", "2018", "2019", "2020", "2021", "12M roll", "category", "2017.1", "2018.1", "2019.1", "2020.1", "2021.1", "12M roll.1", "category") VALUES 
('Debitor 1', 39726.0, 38284.0, 40269.0, 30089.0, 28487.0, 34.299, '↓', 0.5, 0.46, 0.53, 0.46, 0.39, 0.24, '↓'),
('Debitor 2', NULL, NULL, NULL, NULL, 7312.0, 34.15, '↑', NULL, NULL, NULL, NULL, 0.1, 0.24, '↑'),
('Debitor 3', NULL, NULL, NULL, NULL, 2727.0, 14.933, '↑', NULL, NULL, NULL, NULL, 0.04, 0.1, '↑'),
('Debitor 4', NULL, 12904.0, 13258.0, 10332.0, 8182.0, 13.187, '↑', NULL, 0.16, 0.17, 0.16, 0.11, 0.09, '↓'),
('Debitor 5', NULL, NULL, NULL, NULL, NULL, 11.159, '↑', NULL, NULL, NULL, NULL, NULL, 0.08, '↑');

INSERT INTO payment_behavior ("Kunden", "2018", "2019", "2020", "2021", "12M Trend", "Aug 21", "Sep 21", "Okt 21", "Nov 21", "Dez 21", "Jan 22", "Feb 22", "Mär 22", "Apr 22", "Mai 22", "Jun 22", "Jul 22") VALUES 
('alle gewichtet', 1.0, 1.0, 1.0, 1.0, '↓', 50.0, 48.0, 45.0, 40.0, 38.0, 35, 33, 31, 31, 29, 29, 28),
('Debitor 1', 30.0, 30.0, 30.0, 26.0, '↓', 25.0, 25.0, 21.0, 19.0, 19.0, 20, 20, 20, 22, 22, 22, 23),
('Debitor 2', NULL, NULL, NULL, 23.0, '↑', NULL, NULL, NULL, 30.0, 15.0, 18, 22, 26, 26, 27, 28, 28),
('Debitor 3', NULL, NULL, NULL, NULL, '↑', NULL, NULL, NULL, NULL, NULL, 20, 20, 20, 20, 15, 15, 11),
('Debitor 4', 32.0, 27.0, 36.0, 34.0, '↓', 31.0, 31.0, 24.0, 17.0, 19.0, 20, 20, 19, 20, 21, 20, 20);

INSERT INTO income_statement ("category", "2021", "Jan 22", "Feb 22", "Mär 22", "Apr 22", "Mai 22", "Jun 22", "Jul 22", "YTD", "Abw VJ", "Aug 22", "Sep 22", "Okt 22", "Nov 22", "Dez 22", "GESAMT", "Abw VJ.1") VALUES 
('Umsatzerlöse', 5081431.0, 466330.0, 473960.0, 517864.0, 468879.0, 511149.0, 500121.0, 523333.0, 3461635.0, 0.268, 528221.0, 528878.0, 634797.0, 545505.0, 523219.0, 6222255.0, 0.225),
('Bestandsveränderungen', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 40717.0, -13.028, -12.689, NULL, NULL, 15000.0, NULL),
('Andere aktivierte Eigenleistungen', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
('Sonstige betriebliche Erträge', 228640.0, 690.0, 185.0, 603.0, 143.0, 7442.0, -522.0, 6623.0, 15165.0, -0.9309999999999999, 437.0, 396.0, 437.0, 396.0, 18930.0, 35762.0, -0.8440000000000001),
('Gesamtleistung', 5310071.0, 467020.0, 474145.0, 518467.0, 469022.0, 518591.0, 499599.0, 529957.0, 3476800.0, 0.179, 569375.0, 516247.0, 622545.0, 545901.0, 542149.0, 6273016.0, 0.18100000000000002);

INSERT INTO cost_center_analysis ("Kostenstelle", "Kategorie", "Deckungsbeitrag I", "category", "Deckungsbeitrag II", "category", "Deckungsbeitrag III", "category", "RATIOS KOSTEN", "category", "category", "category", "category", "RATIOS PERSONAL", "category", "category", "Mitarbeiter", "category") VALUES 
(NULL, NULL, 'Betrag', 'Marge', 'Betrag', 'Marge', 'Betrag', 'Marge', 'Raum', 'Personal', 'Material', 'Fremd- leistungen', 'sonst. Kosten', 'Kosten pro FTE', 'Umsatz pro FTE', 'Umsatz/ Kosten', 'MA', 'FTE'),
('GESAMT', NULL, 433813, 0.8190000000000001, 42709, 0.081, 36506, 0.069, 0.11, 0.5, 0.18, NULL, 0.14, 2378, 4790, 2.01, 165.0, 109.3),
('Endkostenstellen', NULL, 541780, 0.985, 328365, 0.635, 36506, 0.106, 0.09, 0.22, 0.01, NULL, 0.04, 2286, 9944, 4.35, 129.0, 79.0),
('nicht zugeordnet', NULL, -26.523, NULL, -90.836, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
('Kostenstelle 1', 'Produktion', -81.444, NULL, -170.362, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 2051, -103.0, -0.05, 22.0, 20.4);

INSERT INTO liquidity ("category", "Jul 22", "Aug 22", "Sep 22", "Okt 22", "Nov 22", "Dez 22", "Jan 23", "Feb 23", "Mär 23", "Apr 23", "Mai 23", "Jun 23") VALUES 
('Netto Cashflow', NULL, -24.817, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 15.215, 33.28),
('Kontensaldo inkl. verfügbarer Kasse', -50.284, -39.531, -30.019, -8.652, -14.193, -63.158, -44.916, -30.923, -25.324, -3.111, 15.215, 48.494),
('verfügbare KK Linie (für Folgemonat)', 19.716, 30.469, 39981.0, 61348.0, 55807.0, 6842.0, 25084.0, 39077.0, 44676.0, 66889.0, 70.0, 70.0),
(NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
('Umsatzerlöse', NULL, 528.221, 528878.0, 544797.0, 545505.0, 497164.0, 536782.0, 545612.0, 562900.0, 539409.0, 551.059, 562.893);

INSERT INTO budget_vs_actual ("category", "AKTUELLER MONAT (JULI)", "category", "category", "category", "3 MONATE ROLLIEREND ", "category", "category", "category", "YEAR - TO - DATE", "category", "category", "category", "GESCHÄFTSJAHR", "category", "category", "category") VALUES 
(NULL, 'IST', 'Vorjahr', 'ABWEICHUNG %', NULL, 'IST', 'Vorjahr', 'ABWEICHUNG %', NULL, 'IST', 'Vorjahr', 'ABWEICHUNG %', NULL, 'RFC', 'Vorjahr', 'ABWEICHUNG %', NULL),
('Umsatzerlöse', 523333, 473326, 50007, 0.11, 1534603, 1215666, 318937, 0.26, 3461635, 2730425, 731210, 0.27, 6222255, 5081431, 1140823, 0.22),
('Bestandsveränderungen', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 15000, NULL, 15000, NULL),
('Andere aktivierte Eigenleistungen', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
('Sonstige betriebliche Erträge', 6623, 7080, -457.0, -0.06, 13544, 97182, -83.638, -0.86, 15165, 219734, -204.569, -0.93, 35762, 228640, -192.878, -0.84);