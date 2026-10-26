"""Six authored UI translations; saved identifiers never depend on language."""

import json
from .core import resource_path

LANGUAGE_NAMES = {
    "en": "English",
    "fr": "Français",
    "cs": "Čeština",
    "de": "Deutsch",
    "es": "Español",
    "ja": "日本語",
}
# Each row has one identifier and six translations. Tests check placeholders.
ROWS = """
character|Character|Personnage|Postava|Charakter|Personaje|キャラクター
weapons|Weapons|Armes|Zbraně|Waffen|Armas|武器
stones|Smithing stones|Pierres de forge|Kovářské kameny|Schmiedesteine|Piedras de forja|鍛石
farm|Rune farming|Farm de runes|Získávání run|Runen farmen|Farmeo de runas|ルーン稼ぎ
settings|Settings|Paramètres|Nastavení|Einstellungen|Ajustes|設定
tagline|Plan your next adventure, at your own pace.|Prépare ta prochaine aventure, à ton rythme.|Naplánuj si další dobrodružství vlastním tempem.|Plane dein nächstes Abenteuer in deinem Tempo.|Planifica tu próxima aventura a tu ritmo.|自分のペースで、次の冒険を計画。
character_title|Your next build|Ton prochain build|Tvoje další sestava|Dein nächster Build|Tu próximo build|次のビルド
character_hint|Use permanent attributes, without equipment bonuses. Both levels update automatically.|Utilise les attributs permanents, sans bonus d’équipement. Les deux niveaux se calculent automatiquement.|Zadej trvalé vlastnosti bez bonusů z vybavení. Obě úrovně se vypočítají automaticky.|Nutze dauerhafte Attribute ohne Ausrüstungsboni. Beide Stufen werden automatisch berechnet.|Usa los atributos permanentes, sin bonus de equipo. Ambos niveles se calculan automáticamente.|装備の補正を除いた能力値を入力すると、両方のレベルが自動計算されます。
starting_class|Starting class|Classe de départ|Počáteční povolání|Startklasse|Clase inicial|素性
current_level|Current level|Niveau de départ|Současná úroveň|Aktuelle Stufe|Nivel actual|現在のレベル
target_level|Target level|Niveau visé|Cílová úroveň|Zielstufe|Nivel objetivo|目標レベル
runes_held|Runes held|Runes en poche|Runy u sebe|Vorhandene Runen|Runas disponibles|所持ルーン
attributes|Attributes|Attributs|Vlastnosti|Attribute|Atributos|能力値
attribute|Attribute|Attribut|Vlastnost|Attribut|Atributo|能力値
base|Class base|Base de la classe|Základ povolání|Klassenbasis|Base de clase|素性の初期値
now|Now|Aujourd’hui|Nyní|Jetzt|Actual|現在
goal|Goal|Objectif|Cíl|Ziel|Objetivo|目標
calculate_levels|Calculate levels|Calculer les niveaux|Spočítat úrovně|Stufen berechnen|Calcular niveles|レベルの費用を計算
remaining_cost|Runes to pay|Runes à payer|Zbývající cena|Noch zu zahlen|Runas por pagar|支払うルーン
paid_since_class|Spent since level {base}|Dépensé depuis le niveau {base}|Utraceno od úrovně {base}|Seit Stufe {base} ausgegeben|Gastadas desde el nivel {base}|レベル{base}から消費したルーン
to_maximum|From level {current} to level 713|Du niveau {current} au niveau 713|Z úrovně {current} na úroveň 713|Von Stufe {current} bis Stufe 713|Del nivel {current} al nivel 713|レベル{current}から713まで
level_route|Level {current} → {target} · +{count} level(s)|Niveau {current} → {target} · +{count} niveau(x)|Úroveň {current} → {target} · +{count} úrovní|Stufe {current} → {target} · +{count} Stufen|Nivel {current} → {target} · +{count} niveles|レベル{current} → {target}（+{count}）
budget_route|With your runes: level {current} → {target}, +{count} level(s). Left: {left} runes.|Avec tes runes : niveau {current} → {target}, +{count} niveau(x). Reste : {left} runes.|S tvými runami: úroveň {current} → {target}, +{count} úrovní. Zbude {left} run.|Mit deinen Runen: Stufe {current} → {target}, +{count} Stufen. Übrig: {left} Runen.|Con tus runas: nivel {current} → {target}, +{count} niveles. Sobran {left} runas.|所持ルーンでレベル{current} → {target}（+{count}）。残り：{left}ルーン。
respec|Lower target attributes require rebirth. A Larval Tear is not included.|Les attributs cibles plus bas demandent une renaissance. La larme larvaire n’est pas incluse.|Nižší cílové vlastnosti vyžadují znovuzrození. Larvální slza není započtena.|Niedrigere Zielattribute erfordern eine Wiedergeburt. Die Larventräne ist nicht enthalten.|Los atributos objetivo menores requieren renacer. La lágrima larvaria no está incluida.|能力値を下げるには生まれ直しが必要です。雫の幼生は含まれません。
weapons_title|Your weapon upgrades|Tes améliorations d’armes|Tvoje vylepšení zbraní|Deine Waffenverbesserungen|Tus mejoras de armas|武器の強化計画
weapons_hint|Use a price or choose exact weapons. Stone-shop bell bearings are assumed unlocked.|Utilise un prix ou choisis des armes précises. Les perles de mineur sont supposées débloquées.|Zadej cenu nebo vyber konkrétní zbraně. Zvonečky pro nákup kamenů se považují za odemčené.|Nutze einen Preis oder wähle Waffen. Die Klangperlen für Steine gelten als freigeschaltet.|Usa un precio o elige armas. Se supone que tienes las esferas para comprar piedras.|費用を入力するか武器を選択してください。鍛石購入の鈴玉は入手済みとして計算します。
manual_mode|By upgrade price|À partir du prix|Podle ceny vylepšení|Nach Verbesserungspreis|Por precio de mejora|費用から計算
catalogue_mode|Choose weapons|Choisir des armes|Vybrat zbraně|Waffen auswählen|Elegir armas|武器を選ぶ
choose_weapons|Select your weapons…|Sélectionner tes armes…|Vybrat zbraně…|Waffen auswählen…|Seleccionar armas…|武器を選択…
weapon_type|Weapon type|Type d’arme|Typ zbraně|Waffentyp|Tipo de arma|武器の種類
normal|Normal|Normale|Běžná|Normal|Normal|通常
somber|Somber|Sombre|Ponurá|Dunkel|Sombría|喪色
weapon_name|Weapon name (optional)|Nom de l’arme (facultatif)|Název zbraně (nepovinné)|Waffenname (optional)|Nombre del arma (opcional)|武器名（任意）
base_price|Blacksmith cost: +0 → +1|Prix du forgeron : +0 → +1|Cena u kováře: +0 → +1|Schmiedekosten: +0 → +1|Coste del herrero: +0 → +1|鍛冶の費用：+0 → +1
next_price|Blacksmith cost: +{current} → +{next}|Prix du forgeron : +{current} → +{next}|Cena u kováře: +{current} → +{next}|Schmiedekosten: +{current} → +{next}|Coste del herrero: +{current} → +{next}|鍛冶の費用：+{current} → +{next}
use_next|Use the next upgrade’s price|Utiliser le prix du prochain niveau|Použít cenu dalšího vylepšení|Preis der nächsten Verbesserung nutzen|Usar el precio de la siguiente mejora|次の強化費用を使う
use_base|Use the base price|Utiliser le prix de base|Použít základní cenu|Basispreis nutzen|Usar el precio base|基本費用を使う
current_upgrade|Current upgrade|Amélioration de départ|Současné vylepšení|Aktuelle Verbesserung|Mejora actual|現在の強化値
target_upgrade|Target upgrade|Amélioration visée|Cílové vylepšení|Zielverbesserung|Mejora objetivo|目標の強化値
copies|Copies|Exemplaires|Počet kusů|Exemplare|Ejemplares|本数
max_without_dragon|Maximum without ancient dragon stones|Maximum sans pierres de dragon|Maximum bez dračích kamenů|Maximum ohne Uralte Drachenschmiedesteine|Máximo sin piedras de dragón antiguo|古竜の鍛石を使わず最大強化
calculate_weapons|Calculate upgrades|Calculer les améliorations|Spočítat vylepšení|Verbesserungen berechnen|Calcular mejoras|強化費用を計算
forge_cost|Blacksmith|Forgeron|Kovář|Schmied|Herrero|鍛冶の費用
stone_cost|Stones to buy|Pierres à acheter|Kameny k nákupu|Zu kaufende Steine|Piedras por comprar|購入する鍛石
total_cost|Total rune cost|Coût total en runes|Celková cena v runách|Gesamtkosten in Runen|Coste total en runas|ルーンの合計費用
to_farm|Runes left to farm|Runes restant à farmer|Runy, které je třeba získat|Noch zu farmende Runen|Runas por conseguir|あと稼ぐルーン
recovered_base|Recovered base price: {price} runes.|Prix de base retrouvé : {price} runes.|Vypočtená základní cena: {price} run.|Ermittelter Basispreis: {price} Runen.|Precio base calculado: {price} runas.|逆算した基本費用：{price}ルーン。
standard_warning|Manual prices use a standard profile. Use catalogue cards for weapon-specific prices.|Le prix manuel suit un profil standard. Les cartes du catalogue donnent les tarifs propres aux armes.|Ruční cena používá běžný vzorec. Pro ceny konkrétních zbraní použij katalog.|Manuelle Preise nutzen ein Standardprofil. Waffenabhängige Preise stehen im Katalog.|El precio manual usa un perfil estándar. El catálogo contiene los precios específicos.|手動入力は標準の費用計算を使用します。武器ごとの費用はカタログを使用してください。
dragon_notice|Ancient dragon stones: obtain separately. Their cost and inventory are outside this estimate.|Pierres de dragon : à obtenir séparément. Leur prix et leur stock sont hors estimation.|Prastaré dračí kameny získej zvlášť. Jejich cena a zásoba nejsou zahrnuty.|Uralte Drachenschmiedesteine separat beschaffen. Kosten und Bestand sind nicht enthalten.|Consigue las piedras de dragón aparte. Su precio y existencias no se incluyen.|古竜の鍛石は別途入手してください。価格と所持数は計算の対象外です。
affordable_weapon|With your runes: {route}. Left: {left} runes.|Avec tes runes : {route}. Reste : {left} runes.|S tvými runami: {route}. Zbude {left} run.|Mit deinen Runen: {route}. Übrig: {left} Runen.|Con tus runas: {route}. Sobran {left} runas.|所持ルーンで：{route}。残り：{left}ルーン。
affordable_none|No target fits your runes yet. Left: {left} runes.|Aucune cible ne tient encore dans tes runes. Reste : {left} runes.|Zatím se do tvých run nevejde žádný cíl. Zbude {left} run.|Noch kein Ziel passt zu deinen Runen. Übrig: {left} Runen.|Ningún objetivo cabe aún en tus runas. Sobran {left} runas.|所持ルーンではまだ目標に届きません。残り：{left}ルーン。
selected_count|{count} weapon(s) selected|{count} arme(s) sélectionnée(s)|Vybráno zbraní: {count}|{count} Waffe(n) ausgewählt|{count} arma(s) seleccionada(s)|{count}本を選択中
empty_selection|Choose the weapons you want to improve.|Choisis les armes que tu veux améliorer.|Vyber zbraně, které chceš vylepšit.|Wähle die Waffen, die du verbessern möchtest.|Elige las armas que quieres mejorar.|強化したい武器を選んでください。
search|Search weapons…|Rechercher une arme…|Hledat zbraň…|Waffen suchen…|Buscar un arma…|武器を検索…
all_categories|All categories|Toutes les catégories|Všechny kategorie|Alle Kategorien|Todas las categorías|すべての種類
dlc|DLC|DLC|DLC|DLC|DLC|DLC
yes|Yes|Oui|Ano|Ja|Sí|あり
no|No|Non|Ne|Nein|No|なし
maximum|Max +{level}|Max +{level}|Max +{level}|Max. +{level}|Máx. +{level}|最大 +{level}
done|Done|Terminer|Hotovo|Fertig|Listo|完了
clear_selection|Clear selection|Tout désélectionner|Zrušit výběr|Auswahl aufheben|Quitar selección|選択を解除
catalogue_hint|Click to select a card. Click again to remove it.|Clique pour sélectionner une carte. Reclique pour la retirer.|Kliknutím vyber kartu. Dalším kliknutím ji odebereš.|Klicke zum Auswählen auf eine Karte, erneut zum Abwählen.|Haz clic para seleccionar una tarjeta y otra vez para quitarla.|カードをクリックして選択。もう一度クリックすると解除します。
stones_title|Only the stones you need|Juste les pierres nécessaires|Jen potřebné kameny|Nur die benötigten Steine|Solo las piedras necesarias|必要な鍛石を確認
stones_hint|Unit prices are included in upgrade costs. Double-click a price to change it.|Les prix unitaires sont inclus dans les améliorations. Double-clique un prix pour le modifier.|Jednotkové ceny jsou zahrnuty ve vylepšeních. Dvojklikem můžeš cenu změnit.|Stückpreise sind in den Verbesserungskosten enthalten. Doppelklick zum Ändern.|Los precios unitarios están incluidos en las mejoras. Haz doble clic para cambiarlos.|単価は強化費用に含まれます。変更する場合はダブルクリックしてください。
stone_calculator|Calculate missing stones…|Calculer les pierres manquantes…|Spočítat chybějící kameny…|Fehlende Steine berechnen…|Calcular piedras que faltan…|不足する鍛石を計算…
owned|Owned|En stock|V zásobě|Im Besitz|Disponibles|所持数
required|Required|Nécessaires|Potřeba|Benötigt|Necesarias|必要数
missing|Missing|Manquantes|Chybí|Fehlend|Faltan|不足数
unit_price|Unit price|Prix unitaire|Jednotková cena|Stückpreis|Precio unitario|単価
no_stones|I have no stones|Je n’ai aucune pierre|Nemám žádné kameny|Ich habe keine Steine|No tengo piedras|鍛石を持っていない
apply_stock|Update stone inventory|Mettre à jour le stock|Aktualizovat zásobu kamenů|Steinbestand aktualisieren|Actualizar existencias|所持数を更新
missing_stones|View missing stones…|Voir les pierres manquantes…|Zobrazit chybějící kameny…|Fehlende Steine anzeigen…|Ver piedras que faltan…|不足する鍛石を表示…
bought|Purchased|J’ai acheté|Zakoupeno|Gekauft|Comprada|購入済みにする
complete_upgrades|I’ve upgraded my weapons|J’ai amélioré mes armes|Zbraně jsem vylepšil|Ich habe meine Waffen verbessert|Ya he mejorado mis armas|武器を強化した
stock_hint|Record owned stones. The stock is shared by all selected weapons.|Saisis tes pierres. Le stock est partagé par toutes les armes sélectionnées.|Zadej své kameny. Zásoba je společná pro všechny vybrané zbraně.|Erfasse deine Steine. Der Bestand gilt für alle ausgewählten Waffen.|Introduce tus piedras. Se comparten entre todas las armas seleccionadas.|所持している鍛石は、選択したすべての武器で共有します。
confirm_price|This is the standard shop price. Are you sure you want to change it?|C’est le prix habituel en boutique. Veux-tu vraiment le modifier ?|Toto je běžná cena v obchodě. Opravdu ji chceš změnit?|Dies ist der reguläre Ladenpreis. Möchtest du ihn wirklich ändern?|Este es el precio habitual de la tienda. ¿Seguro que quieres cambiarlo?|通常の販売価格です。本当に変更しますか？
restore_prices|Restore standard prices|Rétablir les prix habituels|Obnovit běžné ceny|Standardpreise wiederherstellen|Restaurar precios habituales|通常価格に戻す
confirm_purchase|Record {quantity} purchased stone(s) for {cost} runes? The cost is deducted from your held runes.|Enregistrer {quantity} pierre(s) achetée(s) pour {cost} runes ? Le coût sera déduit de tes runes en poche.|Zapsat nákup {quantity} kamenů za {cost} run? Částka se odečte od tvých run.|Kauf von {quantity} Stein(en) für {cost} Runen eintragen? Die Kosten werden abgezogen.|¿Registrar {quantity} piedra(s) comprada(s) por {cost} runas? Se descontará el coste.|鍛石{quantity}個を{cost}ルーンで購入したことを記録しますか？ 費用を差し引きます。
confirm_upgrade|Record completed upgrades? Blacksmith runes and required stones are consumed. Surplus stones remain.|Enregistrer les améliorations terminées ? Les runes du forgeron et les pierres nécessaires sont consommées. Le surplus reste.|Zapsat dokončená vylepšení? Odečtou se runy kováře a potřebné kameny. Přebytek zůstane.|Verbesserungen eintragen? Schmiedekosten und benötigte Steine werden abgezogen. Überschüsse bleiben.|¿Registrar las mejoras? Se consumen las runas del herrero y las piedras necesarias. Se conserva el sobrante.|強化の完了を記録しますか？ 鍛冶の費用と必要な鍛石を差し引き、余りは残します。
confirm_dragon|Confirm only if the ancient dragon stones were obtained and used separately.|Confirme seulement si les pierres de dragon ont été obtenues et utilisées séparément.|Potvrď jen pokud jsi prastaré dračí kameny získal a použil zvlášť.|Bestätige nur, wenn du die Uralten Drachenschmiedesteine separat beschafft und verwendet hast.|Confirma solo si has conseguido y usado las piedras de dragón aparte.|古竜の鍛石を別途入手して使用した場合のみ確認してください。
tracked_gain|Runes gained since tracking began: {runes}|Runes gagnées depuis le début du suivi : {runes}|Runy získané od začátku sledování: {runes}|Seit Beginn erhaltene Runen: {runes}|Runas ganadas desde el inicio: {runes}|記録開始後に獲得したルーン：{runes}
farm_title|Measure your route. Plan your time.|Mesure ton parcours. Prévois le temps.|Změř trasu. Naplánuj čas.|Miss deine Route. Plane deine Zeit.|Mide tu ruta. Planifica tu tiempo.|稼ぎを測定し、必要な時間を把握。
farm_hint|Enter the rune difference before and after the test. Include travel and grace resets.|Saisis la différence de runes avant et après le test. Inclus les trajets et retours à la grâce.|Zadej rozdíl run před testem a po něm. Započítej přesuny a návraty k milosti.|Trage die Runendifferenz ein. Reisezeit und Rast am Gnadenort zählen mit.|Introduce la diferencia de runas. Incluye desplazamientos y descansos en la gracia.|測定前後のルーンの差を入力してください。移動や祝福での休息も含めます。
start_minute|Start one minute|Démarrer une minute|Spustit jednu minutu|Eine Minute starten|Iniciar un minuto|1分の測定を開始
stop|Stop|Arrêter|Zastavit|Stoppen|Detener|停止
reset|Reset to one minute|Réinitialiser à une minute|Obnovit jednu minutu|Auf eine Minute zurücksetzen|Restablecer a un minuto|1分にリセット
full_test|Full test: 1 min + 1 min + 3 min|Test complet : 1 min + 1 min + 3 min|Úplný test: 1 min + 1 min + 3 min|Volltest: 1 Min. + 1 Min. + 3 Min.|Prueba completa: 1 min + 1 min + 3 min|総合測定：1分＋1分＋3分
next_test|Start the next test|Démarrer le test suivant|Spustit další test|Nächsten Test starten|Iniciar siguiente prueba|次の測定を開始
record_result|Record this result|Enregistrer ce résultat|Uložit výsledek|Ergebnis speichern|Guardar resultado|測定結果を記録
test_step|Test {index}/3 · {seconds} seconds|Test {index}/3 · {seconds} secondes|Test {index}/3 · {seconds} sekund|Test {index}/3 · {seconds} Sekunden|Prueba {index}/3 · {seconds} segundos|測定{index}/3・{seconds}秒
test_finished|Test finished. Enter your rune gain.|Test terminé. Saisis les runes récoltées.|Test skončil. Zadej získané runy.|Test beendet. Trage die erhaltenen Runen ein.|Prueba terminada. Introduce las runas ganadas.|測定終了。獲得したルーンを入力してください。
full_finished|Full test complete · weighted average over 5 minutes|Test complet terminé · moyenne pondérée sur 5 minutes|Úplný test hotový · vážený průměr za 5 minut|Test abgeschlossen · gewichteter 5-Minuten-Durchschnitt|Prueba completa terminada · media ponderada de 5 minutos|総合測定終了・5分間の加重平均
measured_runes|Runes gained in the test|Runes récoltées pendant le test|Runy získané v testu|Im Test erhaltene Runen|Runas ganadas en la prueba|測定中に獲得したルーン
duration|Measured seconds|Secondes mesurées|Délka měření v sekundách|Gemessene Sekunden|Segundos medidos|測定時間（秒）
efficiency|Sustained efficiency (%)|Rendement soutenu (%)|Dlouhodobá účinnost (%)|Dauerhafte Effizienz (%)|Rendimiento sostenido (%)|継続できるペース（％）
free_goal|Custom rune goal|Objectif libre en runes|Vlastní cíl v runách|Eigenes Runenziel|Objetivo libre de runas|自由な目標ルーン数
goal_combined|Character + weapons|Personnage + armes|Postava + zbraně|Charakter + Waffen|Personaje + armas|キャラクター＋武器
goal_character|Character target|Objectif du personnage|Cíl postavy|Charakterziel|Objetivo del personaje|キャラクターの目標
goal_weapons|Weapon upgrades|Améliorations d’armes|Vylepšení zbraní|Waffenverbesserungen|Mejoras de armas|武器の強化
goal_maximum|Level 713|Niveau 713|Úroveň 713|Stufe 713|Nivel 713|レベル713
goal_free|Custom goal|Objectif libre|Vlastní cíl|Eigenes Ziel|Objetivo libre|自由な目標
talisman|Talisman used in the test|Talisman utilisé pendant le test|Talisman použitý v testu|Talisman im Test|Talismán usado en la prueba|測定時のタリスマン
consumable|Consumable used in the test|Consommable utilisé pendant le test|Spotřební předmět v testu|Verbrauchsgegenstand im Test|Consumible usado en la prueba|測定時の消費アイテム
none|None · +0% runes|Aucun · +0 % de runes|Žádný · +0 % run|Keiner · +0 % Runen|Ninguno · +0 % de runas|なし・ルーン+0％
gold|Gold Scarab · +20% runes|Scarabée d’or · +20 % de runes|Zlatý skarabeus · +20 % run|Goldskarabäus · +20 % Runen|Escarabajo dorado · +20 % de runas|金のスカラベ・ルーン+20％
silver|Silver Scarab · +0% runes|Scarabée d’argent · +0 % de runes|Stříbrný skarabeus · +0 % run|Silberskarabäus · +0 % Runen|Escarabajo plateado · +0 % de runas|銀のスカラベ・ルーン+0％
gold_foot|Gold-Pickled Fowl Foot · +30%|Patte de volaille en saumure dorée · +30 %|Zlatá nakládaná ptačí nožka · +30 %|Goldener Federtierfuß · +30 %|Pata de ave macerada en oro · +30 %|鳥脚の黄金漬け・+30％
silver_foot|Silver-Pickled Fowl Foot · +0% runes|Patte de volaille en saumure argentée · +0 % de runes|Stříbrná nakládaná ptačí nožka · +0 % run|Silberner Federtierfuß · +0 % Runen|Pata de ave macerada en plata · +0 % de runas|鳥脚の白銀漬け・ルーン+0％
gold_horn|Golden Horn Tender · +40%|Corne en saumure dorée · +40 %|Zlatá nakládaná rohovina · +40 %|Goldenes Horn · +40 % Runen|Cuerno macerado en oro · +40 %|角の黄金漬け・+40％
silver_horn|Silver Horn Tender · +0% runes|Corne en saumure argentée · +0 % de runes|Stříbrná nakládaná rohovina · +0 % run|Silberne Hornzartheit · +0 % Runen|Cuerno macerado en plata · +0 % de runas|角の白銀漬け・ルーン+0％
notes|Method and other effects (optional)|Méthode et autres effets (facultatif)|Postup a další účinky (nepovinné)|Methode und weitere Effekte (optional)|Método y otros efectos (opcional)|方法・その他の効果（任意）
estimate|Estimate farming time|Estimer le temps de farm|Odhadnout potřebný čas|Farmzeit schätzen|Estimar tiempo de farmeo|必要な時間を見積もる
rate|Measured runes / minute|Runes mesurées / minute|Naměřené runy za minutu|Gemessene Runen / Minute|Runas medidas / minuto|測定したルーン／分
time_needed|Time to your goal|Temps pour ton objectif|Čas do dosažení cíle|Zeit bis zum Ziel|Tiempo hasta tu objetivo|目標までの時間
without_buffs|Without rune buffs|Sans bonus de runes|Bez bonusů k runám|Ohne Runenboni|Sin bonus de runas|ルーン増加効果なし
with_scarab|Gold Scarab (+20%)|Scarabée d’or (+20 %)|Zlatý skarabeus (+20 %)|Goldskarabäus (+20 %)|Escarabajo dorado (+20 %)|金のスカラベ（+20％）
with_foot|Golden foot (+30%)|Patte dorée (+30 %)|Zlatá nožka (+30 %)|Goldener Fuß (+30 %)|Pata dorada (+30 %)|鳥脚の黄金漬け（+30％）
with_both|Scarab + golden foot (+56%)|Scarabée + patte dorée (+56 %)|Skarabeus + zlatá nožka (+56 %)|Skarabäus + goldener Fuß (+56 %)|Escarabajo + pata dorada (+56 %)|スカラベ＋鳥脚の黄金漬け（+56％）
optimized|Scarab + golden horn (+68%)|Scarabée + corne dorée (+68 %)|Skarabeus + zlatá rohovina (+68 %)|Skarabäus + goldenes Horn (+68 %)|Escarabajo + cuerno dorado (+68 %)|スカラベ＋角の黄金漬け（+68％）
projection_note|Buff comparisons are projections for the same route and uptime. Per-enemy rounding and other effects can change the result. Silver effects improve discovery, not runes.|Les comparaisons sont des projections à parcours et durée des buffs identiques. Les arrondis par ennemi et d’autres effets peuvent modifier le résultat. Les effets argentés améliorent la découverte, pas les runes.|Srovnání je odhad při stejné trase a době účinku. Zaokrouhlení u nepřátel a další efekty mohou výsledek změnit. Stříbrné efekty zvyšují nález předmětů, ne runy.|Prognosen gelten bei gleicher Route und Wirkdauer. Rundungen je Gegner und weitere Effekte können das Ergebnis ändern. Silberne Effekte erhöhen Entdeckung, nicht Runen.|Son proyecciones con la misma ruta y duración. El redondeo por enemigo y otros efectos pueden variar el resultado. Los efectos plateados mejoran el descubrimiento, no las runas.|同じルートで効果を維持した場合の予測です。敵ごとの端数処理や他の効果で変わります。銀の効果は発見力を上げ、ルーンには影響しません。
no_measurement|Record a positive rune gain to see your estimate.|Enregistre un gain de runes pour voir l’estimation.|Pro odhad zadej kladný počet získaných run.|Trage einen positiven Runenertrag für die Schätzung ein.|Registra una ganancia de runas para ver la estimación.|獲得ルーンを入力すると見積もりが表示されます。
settings_title|Make it yours|À ta façon|Podle tvého gusta|Ganz nach deinem Geschmack|A tu manera|自分に合った設定に
language|Language|Langue|Jazyk|Sprache|Idioma|言語
theme|Appearance|Apparence|Vzhled|Darstellung|Apariencia|外観
elden|Antique gold|Or ancien|Staré zlato|Antikgold|Oro antiguo|アンティークゴールド
apply_settings|Apply language and appearance|Appliquer la langue et l’apparence|Použít jazyk a vzhled|Sprache und Darstellung anwenden|Aplicar idioma y apariencia|言語と外観を適用
save_project|Save build project…|Enregistrer le projet de build…|Uložit projekt sestavy…|Build-Projekt speichern…|Guardar proyecto de build…|ビルドを保存…
open_project|Open build project…|Ouvrir un projet de build…|Otevřít projekt sestavy…|Build-Projekt öffnen…|Abrir proyecto de build…|ビルドを開く…
keep_stats|Keep my saved attributes|J’ai les mêmes attributs qu’avant|Ponechat uložené vlastnosti|Gespeicherte Attribute behalten|Mantener atributos guardados|保存した能力値を使う
update_stats|Update my current attributes|Mettre à jour mes attributs de départ|Aktualizovat současné vlastnosti|Aktuelle Attribute ändern|Actualizar atributos actuales|現在の能力値を更新
resume_hint|Your targets stay saved. Update held runes and stones before continuing.|Tes objectifs restent enregistrés. Mets à jour tes runes et tes pierres avant de continuer.|Cíle zůstanou uložené. Před pokračováním aktualizuj runy a kameny.|Deine Ziele bleiben gespeichert. Aktualisiere Runen und Steine vor dem Fortsetzen.|Tus objetivos siguen guardados. Actualiza runas y piedras antes de continuar.|目標は保存されたままです。再開前に所持ルーンと鍛石を更新してください。
autosave_note|Progress stays saved on this computer. Project files let you keep separate builds.|La progression reste enregistrée sur cet ordinateur. Les fichiers de projet permettent de garder plusieurs builds.|Postup zůstává uložený na tomto počítači. Soubory projektu umožňují uchovat více sestav.|Fortschritt bleibt auf diesem Computer gespeichert. Projektdateien ermöglichen mehrere Builds.|El progreso se guarda en este ordenador. Los archivos permiten conservar distintos builds.|進行状況はこのPCに保存されます。プロジェクトファイルで複数のビルドを管理できます。
reset_session|Start a new project|Commencer un nouveau projet|Začít nový projekt|Neues Projekt beginnen|Empezar un nuevo proyecto|新しいプロジェクトを開始
confirm_reset|Start a new project? Save this build first if you want to keep it.|Commencer un nouveau projet ? Enregistre d’abord ce build si tu veux le conserver.|Začít nový projekt? Pokud chceš sestavu zachovat, nejdřív ji ulož.|Neues Projekt beginnen? Speichere diesen Build zuerst, um ihn zu behalten.|¿Empezar un proyecto nuevo? Guarda primero este build si quieres conservarlo.|新しく始めますか？ 現在のビルドを残す場合は先に保存してください。
help|About this version|À propos de cette version|O této verzi|Über diese Version|Acerca de esta versión|このバージョンについて
help_body|Rune costs use the supplied regulation tables. The app is offline. Ancient dragon stones are managed separately. Damage and DPS are not calculated.|Les coûts suivent les tables fournies. L’application est hors ligne. Les pierres de dragon se gèrent séparément. Les dégâts et DPS ne sont pas calculés.|Ceny run vycházejí z dodaných tabulek. Aplikace funguje offline. Prastaré dračí kameny řeš zvlášť. Poškození a DPS se nepočítají.|Runenkosten folgen den mitgelieferten Tabellen. Die App ist offline. Drachenschmiedesteine werden separat verwaltet. Schaden und DPS werden nicht berechnet.|Los costes usan las tablas incluidas. La aplicación es offline. Las piedras de dragón se gestionan aparte. No se calculan daño ni DPS.|費用は付属のデータに基づき、オフラインで動作します。古竜の鍛石は別途管理してください。ダメージやDPSは計算しません。
invalid|Check the numbers, attribute limits and selected upgrades.|Vérifie les nombres, les limites des attributs et les améliorations.|Zkontroluj čísla, omezení vlastností a vybraná vylepšení.|Prüfe Zahlen, Attributgrenzen und Verbesserungen.|Revisa números, límites de atributos y mejoras.|数値、能力値の範囲、強化値を確認してください。
error|Please check your inputs|Vérifie tes saisies|Zkontroluj údaje|Bitte Eingaben prüfen|Revisa los datos|入力内容を確認
io_error|Could not read or save this project. Check the file and location.|Impossible de lire ou enregistrer ce projet. Vérifie le fichier et son emplacement.|Projekt nelze načíst nebo uložit. Zkontroluj soubor a umístění.|Projekt konnte nicht gelesen oder gespeichert werden. Prüfe Datei und Speicherort.|No se pudo leer o guardar el proyecto. Revisa el archivo y su ubicación.|読み込みまたは保存に失敗しました。ファイルと保存先を確認してください。
not_enough|Not enough held runes for this purchase or upgrade.|Pas assez de runes en poche pour cet achat ou cette amélioration.|Na tento nákup nebo vylepšení nemáš dost run.|Nicht genug Runen für diesen Kauf oder diese Verbesserung.|No tienes suficientes runas para esta compra o mejora.|購入または強化に必要な所持ルーンが足りません。
need_stones|Buy or record all missing ordinary stones before confirming upgrades.|Achète ou renseigne toutes les pierres ordinaires manquantes avant de confirmer.|Před potvrzením kup nebo zapiš všechny chybějící běžné kameny.|Kaufe oder erfasse vor der Bestätigung alle fehlenden normalen Steine.|Compra o registra todas las piedras normales que faltan antes de confirmar.|確認する前に、不足する通常の鍛石を購入するか所持数を入力してください。
inverse_error|This cost does not identify a unique standard base. Check the passage or select the exact weapon.|Ce prix ne donne pas une base standard unique. Vérifie le passage ou sélectionne l’arme précise.|Z ceny nelze určit jednoznačný základ. Zkontroluj vylepšení nebo vyber konkrétní zbraň.|Dieser Preis ergibt keinen eindeutigen Basispreis. Prüfe den Schritt oder wähle die konkrete Waffe.|El precio no da una base única. Revisa la mejora o selecciona el arma exacta.|基本費用を一意に逆算できません。強化段階を確認するか武器を選択してください。
ready|Ready for your next adventure|Prêt pour ta prochaine aventure|Připraveno na další dobrodružství|Bereit fürs nächste Abenteuer|Todo listo para tu próxima aventura|次の冒険の準備完了
normal_stone|Smithing Stone [{tier}]|Pierre de forge [{tier}]|Kovářský kámen [{tier}]|Schmiedestein [{tier}]|Piedra de forja [{tier}]|鍛石【{tier}】
somber_stone|Somber Smithing Stone [{tier}]|Pierre de forge sombre [{tier}]|Ponurý kovářský kámen [{tier}]|Dunkelschmiedestein [{tier}]|Piedra de forja sombría [{tier}]|喪色の鍛石【{tier}】
normal_dragon|Ancient Dragon Smithing Stone|Pierre de forge de dragon ancien|Prastarý dračí kovářský kámen|Uralter Drachenschmiedestein|Piedra de forja de dragón antiguo|古竜岩の鍛石
somber_dragon|Somber Ancient Dragon Smithing Stone|Pierre de forge sombre de dragon ancien|Ponurý prastarý dračí kovářský kámen|Uralter Dunkeldrachenschmiedestein|Piedra de forja sombría de dragón antiguo|古竜岩の喪色鍛石
remaining_plan|Your saved goals need {runes} more runes.|Tes objectifs enregistrés demandent encore {runes} runes.|K uloženým cílům zbývá získat {runes} run.|Für deine Ziele fehlen noch {runes} Runen.|Tus objetivos necesitan {runes} runas más.|保存した目標まで、あと{runes}ルーン必要です。
sample_summary|{count} measurement(s), {seconds} seconds in total|{count} mesure(s), {seconds} secondes au total|{count} měření, celkem {seconds} sekund|{count} Messung(en), insgesamt {seconds} Sekunden|{count} medición(es), {seconds} segundos en total|{count}回の測定・合計{seconds}秒
days|d|j|d|T.|d|日
hours|h|h|h|Std.|h|時間
minutes|min|min|min|Min.|min|分
seconds|s|s|s|Sek.|s|秒
vigor|Vigor|Vigueur|Vitalita|Kraft|Vigor|生命力
mind|Mind|Esprit|Mysl|Geist|Mente|精神力
endurance|Endurance|Endurance|Výdrž|Ausdauer|Aguante|持久力
strength|Strength|Force|Síla|Stärke|Fuerza|筋力
dexterity|Dexterity|Dextérité|Obratnost|Geschick|Destreza|技量
intelligence|Intelligence|Intelligence|Inteligence|Weisheit|Inteligencia|知力
faith|Faith|Foi|Víra|Glaube|Fe|信仰
arcane|Arcane|Ésotérisme|Tajemno|Arkanenergie|Arcano|神秘
Vagabond|Vagabond|Vagabond|Tulák|Vagabund|Vagante|放浪騎士
Warrior|Warrior|Guerrier|Válečník|Krieger|Guerrero|剣士
Hero|Hero|Héros|Hrdina|Held|Héroe|勇者
Bandit|Bandit|Bandit|Bandita|Bandit|Bandido|盗賊
Astrologer|Astrologer|Astrologue|Astrolog|Astrologe|Astrólogo|星見
Prophet|Prophet|Prophète|Prorok|Prophet|Profeta|預言者
Samurai|Samurai|Samouraï|Samuraj|Samurai|Samurái|侍
Prisoner|Prisoner|Prisonnier|Vězeň|Gefangener|Prisionero|囚人
Confessor|Confessor|Confesseur|Zpovědník|Bekenner|Confesor|密使
Wretch|Wretch|Indigent|Ubožák|Bettler|Miserable|素寒貧
dagger|Daggers|Dagues|Dýky|Dolche|Dagas|短剣
straight_sword|Straight swords|Épées droites|Rovné meče|Gerade Schwerter|Espadas rectas|直剣
greatsword|Greatswords|Espadons|Velké meče|Großschwerter|Espadones|大剣
colossal_sword|Colossal swords|Épées colossales|Kolosální meče|Kolossalschwerter|Espadas colosales|特大剣
curved_sword|Curved swords|Épées courbes|Zahnuté meče|Krummschwerter|Espadas curvas|曲剣
curved_greatsword|Curved greatswords|Espadons courbes|Velké zahnuté meče|Große Krummschwerter|Espadones curvos|大曲剣
katana|Katanas|Katanas|Katany|Katanas|Katanas|刀
twinblade|Twinblades|Lames doubles|Dvojčepele|Doppelklingen|Hojas dobles|両刃剣
thrusting_sword|Thrusting swords|Épées d’estoc|Bodné meče|Stoßschwerter|Espadas de estoque|刺剣
heavy_thrusting_sword|Heavy thrusting swords|Épées d’estoc lourdes|Těžké bodné meče|Schwere Stoßschwerter|Espadas de estoque pesadas|重刺剣
axe|Axes|Haches|Sekery|Äxte|Hachas|斧
greataxe|Greataxes|Grandes haches|Velké sekery|Großäxte|Grandes hachas|大斧
hammer|Hammers|Marteaux|Kladiva|Hämmer|Martillos|槌
great_hammer|Great hammers|Grands marteaux|Velká kladiva|Großhämmer|Grandes martillos|大槌
flail|Flails|Fléaux|Řemdihy|Flegel|Mayales|フレイル
spear|Spears|Lances|Kopí|Speere|Lanzas|槍
great_spear|Great spears|Grandes lances|Velká kopí|Großspeere|Grandes lanzas|大槍
halberd|Halberds|Hallebardes|Halapartny|Hellebarden|Alabardas|斧槍
reaper|Reapers|Faux|Kosy|Sensen|Guadañas|鎌
fist|Fists|Poings|Pěstní zbraně|Faustwaffen|Puños|拳
claw|Claws|Griffes|Drápy|Klauen|Garras|爪
whip|Whips|Fouets|Biče|Peitschen|Látigos|鞭
colossal_weapon|Colossal weapons|Armes colossales|Kolosální zbraně|Kolossalwaffen|Armas colosales|特大武器
light_bow|Light bows|Arcs courts|Krátké luky|Leichte Bögen|Arcos ligeros|小弓
bow|Bows|Arcs|Luky|Bögen|Arcos|弓
greatbow|Greatbows|Grands arcs|Velké luky|Großbögen|Grandes arcos|大弓
crossbow|Crossbows|Arbalètes|Kuše|Armbrüste|Ballestas|クロスボウ
ballista|Ballistas|Balistes|Balisty|Ballisten|Balistas|バリスタ
glintstone_staff|Glintstone staves|Bâtons de sorcellerie|Hole třpytivého kamene|Schimmersteinstäbe|Bastones de piedra refulgente|杖
sacred_seal|Sacred seals|Sceaux sacrés|Posvátné pečeti|Heilige Siegel|Sellos sagrados|聖印
small_shield|Small shields|Petits boucliers|Malé štíty|Kleine Schilde|Escudos pequeños|小盾
medium_shield|Medium shields|Boucliers moyens|Střední štíty|Mittlere Schilde|Escudos medianos|中盾
greatshield|Greatshields|Grands boucliers|Velké štíty|Großschilde|Grandes escudos|大盾
torch|Torches|Torches|Pochodně|Fackeln|Antorchas|松明
hand_to_hand|Hand-to-hand arts|Arts martiaux|Bojová umění|Kampfkünste|Artes marciales|格闘
perfume_bottle|Perfume bottles|Flacons de parfum|Flakóny parfému|Parfümflaschen|Frascos de perfume|調香瓶
thrusting_shield|Thrusting shields|Boucliers d’estoc|Bodné štíty|Stoßschilde|Escudos de embestida|刺突盾
throwing_blade|Throwing blades|Lames de lancer|Vrhací čepele|Wurfklingen|Hojas arrojadizas|投擲剣
backhand_blade|Backhand blades|Lames inversées|Obrácené čepele|Rückhandklingen|Hojas de revés|逆手剣
light_greatsword|Light greatswords|Espadons légers|Lehké velké meče|Leichte Großschwerter|Espadones ligeros|軽大剣
great_katana|Great katanas|Grands katanas|Velké katany|Großkatanas|Grandes katanas|大刀
beast_claw|Beast claws|Griffes bestiales|Zvířecí drápy|Bestienklauen|Garras de bestia|獣爪
"""
from .style_text import ROWS as EXTRA_ROWS
from .journey_text import ROWS as NEW_ROWS

ROWS = ROWS.strip() + "\n" + EXTRA_ROWS.strip() + "\n" + NEW_ROWS.strip()
TEXT = {language: {} for language in LANGUAGE_NAMES}
for row in ROWS.strip().splitlines():
    key, *values = row.split("|")
    if len(values) != 6:
        raise RuntimeError(f"Invalid translation row: {key}")
    for language, value in zip(TEXT, values):
        TEXT[language][key] = value


from functools import lru_cache


@lru_cache(maxsize=1)
def weapon_names():
    return json.loads(resource_path("assets/weapon_names.json").read_text(encoding="utf-8"))


class Translator:
    def __init__(self, language="en"):
        self.language = language
        self.text = TEXT[language]
        self.names = weapon_names()

    def __call__(self, key, **values):
        return TEXT[self.language].get(key, key).format(**values)

    def t(self, key, **values):
        return self(key, **values)

    def weapon(self, name):
        return self.names.get(self.language, {}).get(name, name)

    def stone(self, key):
        kind, tier = key.split(":")
        return self(kind + "_dragon") if tier == "dragon" else self(kind + "_stone", tier=tier)

    def duration(self, seconds):
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        prefix = f"{days} {self('days')} " if days else ""
        return f"{prefix}{hours:02d} {self('hours')} {minutes:02d} {self('minutes')} {seconds:02d} {self('seconds')}"
