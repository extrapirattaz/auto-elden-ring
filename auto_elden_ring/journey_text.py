"""Additional interface messages, maintained across all six languages."""

ROWS = """
rescan_game|Rescan game saves|Rescanner les sauvegardes|Znovu načíst uložené hry|Spielstände neu einlesen|Volver a leer las partidas|セーブを再スキャン
scan_done|{count} character(s) checked · {events} new event(s)|{count} personnage(s) vérifié(s) · {events} nouvel événement(s)|Zkontrolováno postav: {count} · Nové události: {events}|{count} Charaktere geprüft · {events} neue Ereignisse|{count} personaje(s) comprobado(s) · {events} evento(s) nuevo(s)|{count}キャラクターを確認・新しい記録{events}件
scan_failed|Save unavailable or being written. Previous progress kept; retry after the game saves.|Sauvegarde indisponible ou en cours d’écriture. Progression conservée ; réessaie après la sauvegarde du jeu.|Uložená hra není dostupná nebo se zapisuje. Předchozí postup zůstal zachován; zkuste to po uložení hry.|Spielstand nicht verfügbar oder wird geschrieben. Bisheriger Fortschritt bleibt erhalten; nach dem Speichern erneut versuchen.|Partida no disponible o guardándose. Se conserva el progreso anterior; vuelve a intentarlo cuando termine.|セーブが利用できないか書き込み中です。前の状態を保持しました。ゲームの保存後に再試行してください。
scan_invalid|Finish the current numeric entries, then rescan.|Termine les valeurs numériques en cours, puis relance le rescan.|Dokončete číselné údaje a zkuste znovu načíst uloženou hru.|Zahleneingaben abschließen, dann erneut einlesen.|Completa los valores numéricos y vuelve a leer la partida.|入力中の数値を確定してから再スキャンしてください。
scan_hint|Remembered save locations are checked on startup. Rescan reads the latest disk save while you play; unsaved progress is not available.|Les emplacements enregistrés sont vérifiés au démarrage. Le rescan lit la dernière sauvegarde sur disque pendant que tu joues ; la progression non sauvegardée n’est pas disponible.|Zapamatovaná umístění se kontrolují při spuštění. Opětovné načtení čte poslední uloženou hru na disku i při hraní; neuložený postup není dostupný.|Gespeicherte Pfade werden beim Start geprüft. Während des Spielens wird der letzte Spielstand auf der Festplatte gelesen; ungespeicherter Fortschritt ist nicht verfügbar.|Las rutas guardadas se revisan al iniciar. Puedes leer la última partida del disco mientras juegas; el progreso sin guardar no está disponible.|保存先を起動時に確認します。プレイ中もディスク上の最新セーブを読み込めます。未保存の進行状況は取得できません。
ownership_hint|Blue checks show owned weapons and their saved upgrades/copies. The other check marks weapons selected for your goal.|Les coches bleues indiquent les armes possédées, leurs niveaux enregistrés et les exemplaires. L’autre coche marque les armes choisies pour ton objectif.|Modré značky ukazují vlastněné zbraně, uložená vylepšení a počty. Druhá značka označuje zbraně vybrané pro cíl.|Blaue Häkchen zeigen vorhandene Waffen, gespeicherte Stufen und Stückzahlen. Das andere Häkchen markiert für dein Ziel ausgewählte Waffen.|Las marcas azules muestran armas en posesión, mejoras guardadas y copias. La otra marca señala las elegidas para tu objetivo.|青いチェックは所持武器、保存済みの強化段階と本数を示します。もう一方のチェックは目標に選択した武器を示します。
mini_start|Start|Démarrer|Spustit|Start|Iniciar|開始
mini_reset|Reset|Réinitialiser|Resetovat|Zurücksetzen|Reiniciar|リセット
choose_music|Choose audio file|Choisir un fichier audio|Vybrat zvukový soubor|Audiodatei auswählen|Elegir archivo de audio|音声ファイルを選択
play_music|Play / Resume|Lire / Reprendre|Přehrát / pokračovat|Wiedergabe / Fortsetzen|Reproducir / Continuar|再生 / 再開
choose_profile|Choose a character|Choisis un personnage|Vyberte postavu|Charakter auswählen|Elige un personaje|キャラクターを選択
profile_hint|Create a character, import your saves, or select existing progress.|Crée un personnage, importe tes sauvegardes ou sélectionne une progression existante.|Vytvořte postavu, importujte uložené hry nebo vyberte uložený postup.|Erstelle einen Charakter, importiere Spielstände oder wähle vorhandenen Fortschritt.|Crea un personaje, importa partidas o elige un progreso guardado.|キャラクターを作成するか、セーブを読み込むか、保存済みの進行状況を選択してください。
import_folder|Import installation folder|Importer le dossier d’installation|Importovat instalační složku|Installationsordner importieren|Importar carpeta de instalación|インストール先から読み込む
import_profiles|Import character profiles|Importer les profils de personnages|Importovat profily postav|Charakterprofile importieren|Importar perfiles de personajes|キャラクタープロフィールを読み込む
import_policy_hint|Keep your manually created characters, or replace them with characters from the game? Existing imported characters and their goals are preserved.|Garder tes personnages créés à la main ou les remplacer par ceux du jeu ? Les personnages déjà importés et leurs objectifs sont conservés.|Ponechat ručně vytvořené postavy, nebo je nahradit postavami ze hry? Dříve importované postavy a cíle zůstanou zachovány.|Manuell erstellte Charaktere behalten oder durch Spielcharaktere ersetzen? Bereits importierte Charaktere und Ziele bleiben erhalten.|¿Conservar los personajes creados manualmente o sustituirlos por los del juego? Se conservan los ya importados y sus objetivos.|手動作成したキャラクターを残しますか、ゲームのキャラクターに置き換えますか？読み込み済みのキャラクターと目標は保持されます。
keep_manual|Keep manual profiles and add game characters|Garder les profils manuels et ajouter ceux du jeu|Ponechat ruční profily a přidat postavy ze hry|Manuelle Profile behalten und Spielcharaktere hinzufügen|Conservar perfiles manuales y añadir los del juego|手動プロフィールを残して追加
replace_manual|Replace manual profiles|Remplacer les profils manuels|Nahradit ruční profily|Manuelle Profile ersetzen|Sustituir perfiles manuales|手動プロフィールを置き換える
save_accounts|Detected PC saves|Sauvegardes PC détectées|Nalezené PC uložené hry|Gefundene PC-Spielstände|Partidas de PC detectadas|検出されたPC版セーブ
import_all_saves|Import all detected saves|Importer toutes les sauvegardes détectées|Importovat všechny nalezené hry|Alle gefundenen Spielstände importieren|Importar todas las partidas detectadas|検出したセーブをすべて読み込む
owned|Owned|Possédée|Vlastněná|Im Besitz|En posesión|所持
not_owned|Not in saved inventory|Absente de l’inventaire enregistré|Není v uloženém inventáři|Nicht im gespeicherten Inventar|No está en el inventario guardado|保存済みの所持品にはありません
all_stones|I have all missing stones|J’ai toutes les pierres manquantes|Mám všechny chybějící kameny|Ich habe alle fehlenden Steine|Tengo todas las piedras que faltan|不足していた石はすべて入手済み
previous_page|Previous|Précédent|Předchozí|Zurück|Anterior|前へ
next_page|Next|Suivant|Další|Weiter|Siguiente|次へ
music_hint|Local MP3, WAV, FLAC and OGG playback. Play resumes after Pause; choosing another file releases the previous track.|Lecture locale MP3, WAV, FLAC et OGG. Play reprend après Pause ; changer de fichier libère le morceau précédent.|Přehrávání místních MP3, WAV, FLAC a OGG. Přehrát pokračuje po pauze; nový soubor uvolní předchozí skladbu.|Lokale MP3-, WAV-, FLAC- und OGG-Wiedergabe. Wiedergabe setzt nach Pause fort; ein neuer Titel gibt den vorherigen frei.|Reproducción local de MP3, WAV, FLAC y OGG. Reproducir continúa tras Pausa; elegir otro archivo libera la pista anterior.|ローカルのMP3、WAV、FLAC、OGGに対応。再生で一時停止から再開し、別のファイルを選ぶと前の曲を解放します。
farm_current_level|Current level|Niveau actuel|Současná úroveň|Aktuelle Stufe|Nivel actual|現在のレベル
invested_runes|Runes already invested since your starting class|Runes déjà investies depuis la classe de départ|Runy již investované od počáteční třídy|Seit der Startklasse investierte Runen|Runas ya invertidas desde la clase inicial|初期クラスから消費したルーン
invested_farm_time|Equivalent farming time for invested runes|Temps de farm équivalent aux runes déjà investies|Odpovídající doba farmení investovaných run|Entsprechende Farmzeit für investierte Runen|Tiempo de farmeo equivalente a las runas invertidas|消費済みルーンに相当する稼ぎ時間
newer_events|Show newer events|Afficher les événements suivants|Zobrazit novější události|Neuere Ereignisse anzeigen|Mostrar eventos posteriores|新しいイベントを表示
runes|Runes|Runes|Runy|Runen|Runas|ルーン
weapon_acquired|Acquired|Récupérée|Získaná|Erhalten|Obtenida|入手
weapon_upgraded|Upgraded|Améliorée|Vylepšená|Verbessert|Mejorada|強化
autosave_note|Progress and character timelines are saved automatically on this computer.|La progression et les frises de tes personnages sont enregistrées automatiquement sur cet ordinateur.|Postup a historie postav se automaticky ukládají v tomto počítači.|Fortschritt und Charakter-Zeitleisten werden automatisch auf diesem Computer gespeichert.|El progreso y las cronologías se guardan automáticamente en este equipo.|進行状況とキャラクターの履歴は、このパソコンに自動保存されます。
older_events|Show older events|Afficher les événements précédents|Zobrazit starší události|Ältere Ereignisse anzeigen|Mostrar eventos anteriores|以前のイベントを表示
add_event|Add event|Ajouter un événement|Přidat událost|Ereignis hinzufügen|Añadir evento|イベントを追加
current_event|Save current progress|Enregistrer la progression actuelle|Uložit aktuální postup|Aktuellen Fortschritt speichern|Guardar progreso actual|現在の進行状況を保存
custom_event|Custom event|Événement personnalisé|Vlastní událost|Eigenes Ereignis|Evento personalizado|カスタムイベント
empty_profiles|Create a character or import a save to start your timeline.|Crée un personnage ou importe une sauvegarde pour commencer ta frise.|Vytvořte postavu nebo importujte uloženou hru.|Erstelle einen Charakter oder importiere einen Spielstand.|Crea un personaje o importa una partida para empezar.|キャラクターを作成するかセーブを読み込んで始めましょう。
import_save|Import game save|Importer une sauvegarde du jeu|Importovat uloženou hru|Spielstand importieren|Importar partida|セーブを読み込む
refresh_save|Refresh from save|Actualiser depuis la sauvegarde|Aktualizovat z uložené hry|Aus Spielstand aktualisieren|Actualizar desde la partida|セーブから更新
save_hint|Choose the game folder, then its PC save. Saves are read only; no game file is modified.|Choisis le dossier du jeu puis sa sauvegarde PC. Lecture seule : aucun fichier du jeu n’est modifié.|Vyberte složku hry a PC uloženou hru. Soubory se pouze čtou.|Wähle den Spielordner und den PC-Spielstand. Dateien werden nur gelesen.|Elige la carpeta del juego y su partida de PC. Solo lectura.|ゲームのフォルダーとPC版セーブを選択。ファイルは変更しません。
game_folder|Game installation folder|Dossier d’installation du jeu|Instalační složka hry|Installationsordner|Carpeta de instalación|ゲームのインストール先
select_save|Select .sl2 / .co2 save|Choisir une sauvegarde .sl2 / .co2|Vybrat .sl2 / .co2|.sl2 / .co2 auswählen|Seleccionar .sl2 / .co2|.sl2 / .co2 を選択
importing|Reading the save…|Lecture de la sauvegarde…|Čtení uložené hry…|Spielstand wird gelesen…|Leyendo la partida…|セーブを読み込み中…
date_simple|Date and time (DD/MM/YYYY HH:MM)|Date et heure (JJ/MM/AAAA HH:MM)|Datum a čas (DD/MM/RRRR HH:MM)|Datum und Uhrzeit (TT/MM/JJJJ HH:MM)|Fecha y hora (DD/MM/AAAA HH:MM)|日時 (日/月/年 時:分)
owned_weapons|Acquired weapons|Armes récupérées|Získané zbraně|Erhaltene Waffen|Armas obtenidas|入手した武器
add_weapon|Add acquired / upgraded weapon|Ajouter une arme récupérée / améliorée|Přidat získanou / vylepšenou zbraň|Erhaltene / verbesserte Waffe hinzufügen|Añadir arma obtenida / mejorada|入手・強化した武器を追加
save_import|Imported game progress|Progression importée du jeu|Importovaný postup|Importierter Spielfortschritt|Progreso importado|ゲームから読み込んだ進行状況
upgrade_event|Weapons upgraded|Armes améliorées|Zbraně vylepšeny|Waffen verbessert|Armas mejoradas|武器を強化
farm_spot|Farming spot|Spot de farm|Místo farmení|Farm-Ort|Lugar de farmeo|稼ぎ場所
save_spot|Save this farming spot|Enregistrer ce spot de farm|Uložit toto místo|Farm-Ort speichern|Guardar este lugar|この稼ぎ場所を保存
spot_name|Spot name|Nom du spot|Název místa|Name des Farm-Orts|Nombre del lugar|場所の名前
new_measurement|Current measurement|Mesure actuelle|Aktuální měření|Aktuelle Messung|Medición actual|現在の測定
small_mode|Small companion|Mini compagnon|Malý pomocník|Kleiner Begleiter|Compañero compacto|ミニコンパニオン
full_window|Open full application|Ouvrir l’application complète|Otevřít celou aplikaci|Vollständige Anwendung öffnen|Abrir aplicación completa|通常ウィンドウを開く
import_unverified|Import reads your latest saved progress, not live game memory. Unrecognized inventory items are reported separately.|L’import lit ta dernière sauvegarde, pas la mémoire du jeu en direct. Les objets non reconnus sont indiqués séparément.|Import čte uložený stav, ne živou paměť hry. Neznámé předměty jsou uvedeny zvlášť.|Der Import liest den gespeicherten Stand, nicht den laufenden Speicher. Unbekannte Gegenstände werden separat angezeigt.|Se lee la última partida guardada, no la memoria en vivo. Los objetos desconocidos se indican aparte.|最新のセーブを読み込みます。リアルタイムのメモリーではありません。不明なアイテムは別途表示します。
unknown_items|Unrecognized items: {count}|Objets non reconnus : {count}|Neznámé předměty: {count}|Unbekannte Gegenstände: {count}|Objetos no reconocidos: {count}|不明なアイテム: {count}
changes|Changes since previous event|Changements depuis l’événement précédent|Změny od předchozí události|Änderungen seit dem letzten Ereignis|Cambios desde el evento anterior|前回のイベントからの変更
back|Back|Retour|Zpět|Zurück|Volver|戻る
equipment|Equipment|Équipement|Vybavení|Ausrüstung|Equipo|装備
armor|Armor|Armures|Zbroj|Rüstungen|Armaduras|防具
items|Items|Objets|Předměty|Gegenstände|Objetos|アイテム
equipped|Currently equipped|Équipement porté|Aktuálně vybaveno|Aktuell ausgerüstet|Equipo actual|現在の装備
empty_equipment|No saved equipment data. Import a game save to read equipped items.|Aucun équipement enregistré. Importe une sauvegarde pour lire les objets équipés.|Žádná uložená výbava. Importujte uloženou hru.|Keine gespeicherte Ausrüstung. Importiere einen Spielstand.|Sin equipo guardado. Importa una partida.|装備データがありません。セーブを読み込んでください。
unknown_item_id|Unresolved item · ID {id}|Objet non identifié · ID {id}|Neznámý předmět · ID {id}|Unbekannter Gegenstand · ID {id}|Objeto sin identificar · ID {id}|未識別アイテム · ID {id}
bearings|Smithing bell bearings|Perles de mineur|Zvony horníků|Klangperlen der Schmiedesteinschürfer|Esferas de minero|鍛石掘りの鈴玉
bearing_unknown|Not held. Delivery to the shop is not verified.|Non portée. Remise à la boutique non vérifiée.|Není v inventáři. Odevzdání obchodu není ověřeno.|Nicht im Inventar. Abgabe im Laden nicht geprüft.|No está en el inventario. Entrega a la tienda sin verificar.|所持品にはありません。店への納品状況は未確認です。
"""
