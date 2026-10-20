const tg = window.Telegram.WebApp;

tg.ready();   // Сообщаем Telegram, что приложение загрузилось
tg.expand();  // Раскрываем приложение на весь экран
tg.setHeaderColor('#0d1730');
tg.setBackgroundColor('#14213d');

let currentScreen = 'arena';     // Главный экран — лиги (центральная кнопка)
let previousScreen = 'arena';    // Куда вернуться из профиля и новостей по кнопке "Назад"
let profile = null;


// ---------- Запросы к серверу ----------

// GET-запрос к API бота. В заголовке передаём initData — по нему сервер узнаёт игрока
async function apiGet(url) {
    const response = await fetch(url, {
        headers: { 'X-Init-Data': tg.initData }
    });
    const data = await response.json();
    return { status: response.status, data: data };
}

// POST-запрос к API бота (body — данные, которые отправляем)
async function apiPost(url, body) {
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'X-Init-Data': tg.initData, 'Content-Type': 'application/json' },
        body: JSON.stringify(body || {})
    });
    const data = await response.json();
    return { status: response.status, data: data };
}

// Показываем ошибку от сервера. true — если ошибка была
function handleError(result) {
    if (result.status === 200) {
        return false;
    }

    if (result.data.error === 'not_subscribed') {
        tg.showConfirm('Чтобы продолжить, подпишитесь на наш канал. Открыть канал?', function (ok) {
            if (ok) {
                tg.openTelegramLink(result.data.channel);
            }
        });
        return true;
    }

    tg.showAlert(result.data.error || 'Что-то пошло не так, попробуйте ещё раз');
    return true;
}


// ---------- Навигация ----------

function showScreen(name) {
    // Профиль и новости открываются поверх — запоминаем, куда вернуться
    const overlay = name === 'profile' || name === 'news';
    if (overlay && currentScreen !== 'profile' && currentScreen !== 'news') {
        previousScreen = currentScreen;
    }

    // Прячем все экраны и показываем нужный
    const screens = document.querySelectorAll('.screen');
    for (const screen of screens) {
        screen.classList.add('hidden');
    }
    document.getElementById('screen-' + name).classList.remove('hidden');

    // Подсвечиваем активную кнопку снизу
    const tabs = document.querySelectorAll('.tab');
    for (const tab of tabs) {
        if (tab.dataset.screen === name) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    }

    // Круглые кнопки (счёт и ежедневная награда) — только на главном экране
    const scoreButton = document.getElementById('score-fab');
    const dailyButton = document.getElementById('daily-fab');
    if (name === 'arena') {
        scoreButton.classList.remove('hidden');
        dailyButton.classList.remove('hidden');
    } else {
        scoreButton.classList.add('hidden');
        dailyButton.classList.add('hidden');
    }

    // Аватар подсвечен, когда открыт профиль
    const avatarButton = document.getElementById('avatar-btn');
    if (name === 'profile') {
        avatarButton.classList.add('active');
    } else {
        avatarButton.classList.remove('active');
    }

    if (overlay) {
        tg.BackButton.show();
    } else {
        tg.BackButton.hide();
    }

    currentScreen = name;
    window.scrollTo(0, 0);
}

function setupNavigation() {
    const tabs = document.querySelectorAll('.tab');
    for (const tab of tabs) {
        tab.addEventListener('click', function () {
            tg.HapticFeedback.selectionChanged();
            showScreen(tab.dataset.screen);
        });
    }

    document.getElementById('avatar-btn').addEventListener('click', function () {
        tg.HapticFeedback.selectionChanged();
        showScreen('profile');
    });

    document.getElementById('news-btn').addEventListener('click', function () {
        tg.HapticFeedback.selectionChanged();
        openNews();
    });

    document.getElementById('daily-fab').addEventListener('click', claimDaily);

    // Кнопка "Назад" в шапке Telegram: из профиля возвращаемся на прошлый экран
    tg.BackButton.onClick(function () {
        showScreen(previousScreen);
    });
}


// ---------- Профиль ----------

function fillProfile() {
    // Фото берём из Telegram (если пользователь разрешил его показывать)
    const tgUser = tg.initDataUnsafe.user;
    if (tgUser && tgUser.photo_url) {
        document.getElementById('avatar').src = tgUser.photo_url;
        document.getElementById('profile-avatar').src = tgUser.photo_url;
    }

    // textContent, а не innerHTML — так имя игрока не сможет сломать страницу
    document.getElementById('topbar-name').textContent = profile.name;
    document.getElementById('coins').textContent = profile.gold;
    document.getElementById('crystals').textContent = profile.crystals;

    document.getElementById('profile-name').textContent = profile.name;
    if (profile.link) {
        document.getElementById('profile-link').textContent = profile.link.replace('https://t.me/', '@');
    }
    document.getElementById('profile-division').textContent = profile.division;
    document.getElementById('profile-rating').textContent = profile.rating !== null ? profile.rating : '—';

    const info = [];
    if (profile.sex) {
        info.push('Пол: ' + profile.sex);
    }
    if (profile.age) {
        info.push('Возраст: ' + profile.age);
    }
    document.getElementById('profile-info').textContent = info.join(' · ');

    if (profile.ban_until) {
        const ban = document.getElementById('profile-ban');
        ban.textContent = '❌ Бан до ' + profile.ban_until;
        ban.classList.remove('hidden');
    }

    // История турниров
    const tournaments = document.getElementById('profile-tournaments');
    tournaments.innerHTML = '';
    if (profile.tournaments.length === 0) {
        tournaments.textContent = 'не участвовал(-а) 🥲';
    }
    for (const name of profile.tournaments) {
        const chip = document.createElement('span');
        chip.className = 'chip';
        chip.textContent = name;
        tournaments.appendChild(chip);
    }

    // Рефералы
    document.getElementById('profile-friends').textContent = profile.friends;
    document.getElementById('profile-friends-played').textContent = profile.friends_played;
    document.getElementById('profile-ref-rules').textContent = '+' + profile.referral_gold + ' 🪙 и +' + profile.referral_crystals + ' 💎 за каждого друга. Награда придёт, когда друг закончит регистрацию и сыграет первую игру — с соперником или в турнире';
    document.getElementById('profile-ref-link').textContent = profile.referral_link;

    // Серия заходов
    document.getElementById('profile-streak').textContent = profile.streak;
    document.getElementById('profile-best-streak').textContent = profile.best_streak;
}

function fillHistory(items) {
    const container = document.getElementById('profile-history');
    container.innerHTML = '';

    if (items.length === 0) {
        container.textContent = 'Пока пусто — сыграй матч или пригласи друга';
        container.className = 'history muted';
        return;
    }

    for (const item of items) {
        const row = document.createElement('div');
        row.className = 'history-item';

        const text = document.createElement('div');
        text.textContent = item.date + ' · ' + item.comment;

        const amount = document.createElement('div');
        if (item.amount > 0) {
            amount.className = 'history-amount plus';
            amount.textContent = '+' + item.amount + ' 🪙';
        } else {
            amount.className = 'history-amount minus';
            amount.textContent = item.amount + ' 🪙';
        }

        row.appendChild(text);
        row.appendChild(amount);
        container.appendChild(row);
    }
}

function setupReferralButtons() {
    document.getElementById('btn-copy-ref').addEventListener('click', async function () {
        try {
            await navigator.clipboard.writeText(profile.referral_link);
            tg.HapticFeedback.notificationOccurred('success');
            tg.showAlert('Ссылка скопирована!');
        } catch (error) {
            tg.showAlert(profile.referral_link);
        }
    });

    document.getElementById('btn-share-ref').addEventListener('click', function () {
        const text = 'Присоединяйся к нашему теннисному клубу 🎾 и участвуй в турнирах! 🏆';
        const shareUrl = 'https://t.me/share/url?url=' + encodeURIComponent(profile.referral_link) + '&text=' + encodeURIComponent(text);
        tg.openTelegramLink(shareUrl);
    });
}


// ---------- Лиги ----------

function fillLeague() {
    const leagues = profile.leagues;
    const number = profile.league;          // Текущая лига (1-10)
    const current = leagues[number - 1];

    document.getElementById('league-picture').src = '/static/img/locations/' + number + '.svg';
    document.getElementById('league-name').textContent = 'Лига ' + number + ': ' + current.name;

    // Прогресс до следующей лиги
    const fill = document.getElementById('league-progress');
    const progressText = document.getElementById('league-progress-text');
    const nextText = document.getElementById('league-next');

    if (number === leagues.length) {
        fill.style.width = '100%';
        progressText.textContent = profile.season_gold + ' 🪙';
        nextText.textContent = 'Ты в высшей лиге! 🏆';
    } else {
        const next = leagues[number];
        const done = profile.season_gold - current.from;
        const need = next.from - current.from;
        fill.style.width = Math.floor(done / need * 100) + '%';
        progressText.textContent = profile.season_gold + ' / ' + next.from + ' 🪙';
        nextText.textContent = 'До лиги «' + next.name + '» осталось ' + (next.from - profile.season_gold) + ' 🪙';
    }

    // Список всех локаций
    const container = document.getElementById('locations');
    container.innerHTML = '';

    for (let i = 0; i < leagues.length; i++) {
        const leagueNumber = i + 1;
        const locked = leagueNumber > number;

        const card = document.createElement('div');
        card.className = 'location';
        if (locked) {
            card.classList.add('locked');
        }
        if (leagueNumber === number) {
            card.classList.add('current');
        }

        const picture = document.createElement('img');
        picture.className = 'location-picture';
        picture.src = '/static/img/locations/' + leagueNumber + '.svg';
        picture.alt = leagues[i].name;
        card.appendChild(picture);

        if (locked) {
            const lock = document.createElement('img');
            lock.className = 'location-lock';
            lock.src = '/static/img/icons/lock.svg';
            lock.alt = '';
            card.appendChild(lock);
        }

        const name = document.createElement('div');
        name.className = 'location-name';

        const title = document.createElement('span');
        title.textContent = leagueNumber + '. ' + leagues[i].name;
        if (leagueNumber === number) {
            title.textContent += ' — ты здесь';
        }

        const from = document.createElement('span');
        from.className = 'location-from';
        from.textContent = 'от ' + leagues[i].from + ' 🪙';

        name.appendChild(title);
        name.appendChild(from);
        card.appendChild(name);

        container.appendChild(card);
    }
}


// ---------- Ежедневная награда ----------

// Красный кружок на подарке, если награду ещё не забрали
function fillDaily() {
    const dot = document.getElementById('daily-dot');
    if (profile.daily_available) {
        dot.classList.remove('hidden');
    } else {
        dot.classList.add('hidden');
    }
}

async function claimDaily() {
    tg.HapticFeedback.selectionChanged();

    if (!profile.daily_available) {
        tg.showAlert('Сегодня награда уже получена 🎁 Приходите завтра! Серия: ' + profile.streak + ' дн. подряд 🔥');
        return;
    }

    const result = await apiPost('/api/visit');
    if (handleError(result)) {
        return;
    }

    showReward(result.data, function () {});
    await reloadProfile();
}

// Обновить профиль, монеты, лигу и историю (после награды)
async function reloadProfile() {
    const result = await apiGet('/api/me');
    if (result.status !== 200) {
        return;
    }
    profile = result.data;
    fillProfile();
    fillLeague();
    fillDaily();
    fillNewsDot();

    const history = await apiGet('/api/gold_history');
    fillHistory(history.data);
}


// ---------- Новости ----------

function fillNewsDot() {
    const dot = document.getElementById('news-dot');
    if (profile.unread_news > 0) {
        dot.classList.remove('hidden');
    } else {
        dot.classList.add('hidden');
    }
}

async function openNews() {
    showScreen('news');

    const list = document.getElementById('news-list');
    list.innerHTML = '';

    const result = await apiGet('/api/news');
    if (result.status !== 200) {
        return;
    }

    if (result.data.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'empty';
        empty.textContent = 'Новостей пока нет';
        list.appendChild(empty);
    }

    for (const news of result.data) {
        const box = document.createElement('div');
        box.className = 'card';
        if (news.is_new) {
            box.classList.add('news-new');
        }

        const date = document.createElement('div');
        date.className = 'muted';
        date.textContent = (news.is_new ? '🔴 Новое · ' : '') + news.date;
        box.appendChild(date);

        if (news.photo) {
            const photo = document.createElement('img');
            photo.className = 'news-photo';
            photo.src = news.photo;
            photo.alt = '';
            box.appendChild(photo);
        }

        if (news.text) {
            const text = document.createElement('div');
            text.className = 'news-text';
            text.textContent = news.text;
            box.appendChild(text);
        }

        if (news.link_url) {
            const button = document.createElement('button');
            button.className = 'btn btn-gold btn-wide';
            button.type = 'button';
            button.textContent = news.link_text || 'Открыть';
            button.addEventListener('click', function () {
                if (news.link_url.startsWith('https://t.me/')) {
                    tg.openTelegramLink(news.link_url);
                } else {
                    tg.openLink(news.link_url);
                }
            });
            box.appendChild(button);
        }

        list.appendChild(box);
    }

    // Отмечаем прочитанными — красный кружок пропадает
    await apiPost('/api/news_seen');
    profile.unread_news = 0;
    fillNewsDot();
}

function showReward(reward, onClose) {
    if (reward.gold === 0) {
        onClose();  // Сегодня награду уже получали
        return;
    }

    document.getElementById('reward-title').textContent = 'Серия: ' + reward.streak + ' дн. подряд';

    const lines = document.getElementById('reward-lines');
    lines.innerHTML = '';

    const daily = document.createElement('div');
    daily.textContent = 'Ежедневная награда: +' + reward.gold + ' 🪙';
    lines.appendChild(daily);

    if (reward.bonus > 0) {
        const bonus = document.createElement('div');
        bonus.className = 'plus';
        bonus.textContent = 'Бонус за ' + reward.streak + ' дней: +' + reward.bonus + ' 🪙';
        lines.appendChild(bonus);
    }

    const modal = document.getElementById('reward-modal');
    modal.classList.remove('hidden');
    tg.HapticFeedback.notificationOccurred('success');

    document.getElementById('reward-ok').onclick = function () {
        modal.classList.add('hidden');
        onClose();
    };
}


// ---------- Итоги года с салютом ----------

function showSeasonSummary() {
    const summary = profile.season_summary;
    if (!summary) {
        return;
    }

    const league = profile.leagues[summary.league - 1];
    document.getElementById('season-title').textContent = 'Итоги ' + summary.year + ' года 🎉';
    document.getElementById('season-picture').src = '/static/img/locations/' + summary.league + '.svg';
    document.getElementById('season-league').textContent = 'Лига ' + summary.league + ': ' + league.name;
    document.getElementById('season-text').textContent = 'За год ты заработал(-а) ' + summary.gold + ' 🪙. Лиги обнулились — монеты и скины остались с тобой. Вперёд за новой вершиной!';

    const modal = document.getElementById('season-modal');
    modal.classList.remove('hidden');
    startFireworks();

    document.getElementById('season-ok').onclick = async function () {
        modal.classList.add('hidden');
        stopFireworks();
        await apiPost('/api/season_seen');
    };
}

let fireworksTimer = null;

function startFireworks() {
    const canvas = document.getElementById('fireworks');
    const context = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const colors = ['#ffc83d', '#ff6b9d', '#7fdbff', '#2ecc71', '#b15cff', '#ffffff'];
    let sparks = [];

    fireworksTimer = setInterval(function () {
        // Иногда запускаем новый залп в случайном месте
        if (Math.random() < 0.06) {
            const x = Math.random() * canvas.width;
            const y = Math.random() * canvas.height * 0.5;
            const color = colors[Math.floor(Math.random() * colors.length)];

            for (let i = 0; i < 40; i++) {
                const angle = Math.PI * 2 * i / 40;
                const speed = 2 + Math.random() * 2;
                sparks.push({ x: x, y: y, dx: Math.cos(angle) * speed, dy: Math.sin(angle) * speed, life: 60, color: color });
            }
        }

        context.clearRect(0, 0, canvas.width, canvas.height);

        const alive = [];
        for (const spark of sparks) {
            spark.x += spark.dx;
            spark.y += spark.dy;
            spark.dy += 0.05;  // Искры падают вниз
            spark.life -= 1;

            if (spark.life > 0) {
                context.globalAlpha = spark.life / 60;
                context.fillStyle = spark.color;
                context.fillRect(spark.x, spark.y, 3, 3);
                alive.push(spark);
            }
        }
        sparks = alive;
    }, 16);
}

function stopFireworks() {
    clearInterval(fireworksTimer);
}


// ---------- Турнир ----------

let tournamentData = null;
let selectedTournament = null;

// Что показать под турниром в зависимости от статуса
const TOURNAMENT_STATUS = {
    'pending': '⏳ Чек на проверке у редактора',
    'registered': '✅ Вы участвуете',
    'banned': '❌ Нельзя участвовать из-за бана',
    'no_division': '⚠️ Сначала нужно получить дивизион — напишите редактору',
    'wrong_division': '⚠️ Турнир не для вашего дивизиона',
    'full': '🥲 Мест в вашем дивизионе больше нет'
};

function tournamentDetails(tournament) {
    let text = '💪 Дивизион: ' + tournament.divisions + '\n🎾 Тип: ' + tournament.type + '\n🙋‍♂️ Участников в дивизионе: до ' + tournament.quantity + '\n📅 ' + tournament.start;
    if (tournament.end) {
        text += ' — ' + tournament.end;
    }
    text += '\n💰 Взнос: ' + tournament.price + ' бел.руб.';
    return text;
}

function tournamentCard(tournament) {
    const box = document.createElement('div');
    box.className = 'card';

    const title = document.createElement('div');
    title.className = 'match-date';
    title.textContent = '🏆 ' + tournament.name;
    box.appendChild(title);

    const details = document.createElement('div');
    details.className = 'match-line pay-path';
    details.textContent = tournamentDetails(tournament);
    box.appendChild(details);

    if (tournament.status === 'can_register' || tournament.status === 'can_register_second') {
        const button = document.createElement('button');
        button.className = 'btn btn-gold btn-wide tournament-card-button';
        button.type = 'button';
        if (tournament.status === 'can_register') {
            button.textContent = 'Записаться';
        } else {
            button.textContent = 'Записаться ещё в дивизион «' + tournament.division_name + '»';
        }
        button.addEventListener('click', function () {
            openTournamentModal(tournament);
        });
        box.appendChild(button);
    } else {
        const status = document.createElement('div');
        status.className = 'status tournament-card-button';
        status.textContent = TOURNAMENT_STATUS[tournament.status];
        box.appendChild(status);
    }

    return box;
}

// Карточка идущего турнира (вкладка "Активные турниры")
function runningCard(tournament) {
    const box = document.createElement('div');
    box.className = 'card';

    const title = document.createElement('div');
    title.className = 'match-date';
    title.textContent = '🏆 ' + tournament.name;
    box.appendChild(title);

    const dates = document.createElement('div');
    dates.className = 'match-line';
    dates.textContent = '📅 ' + tournament.start + (tournament.end ? ' — ' + tournament.end : '') + ' · соперников: ' + tournament.players.length;
    box.appendChild(dates);

    if (tournament.link) {
        const button = document.createElement('button');
        button.className = 'btn btn-wide tournament-card-button';
        button.type = 'button';
        button.textContent = '📋 Турнирная таблица';
        button.addEventListener('click', function () {
            tg.openLink(tournament.link);
        });
        box.appendChild(button);
    }

    return box;
}

function tableButton(table) {
    const button = document.createElement('button');
    button.className = 'btn table-link';
    button.type = 'button';
    button.textContent = '📋 ' + table.name;
    button.addEventListener('click', function () {
        tg.openLink(table.link);
    });
    return button;
}

function fillTournaments() {
    const list = document.getElementById('tournament-list');
    list.innerHTML = '';

    if (tournamentData.tournaments.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'empty';
        empty.textContent = 'Сейчас нет турниров, на которые идёт запись 🥲';
        list.appendChild(empty);
    }
    for (const tournament of tournamentData.tournaments) {
        list.appendChild(tournamentCard(tournament));
    }

    // Таблицы
    const tables = document.getElementById('tournament-tables');
    tables.innerHTML = '';

    const activeTitle = document.createElement('div');
    activeTitle.className = 'section-title';
    activeTitle.textContent = 'Активные турниры';
    tables.appendChild(activeTitle);
    if (tournamentData.active_tables.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'muted';
        empty.textContent = 'Пока нет';
        tables.appendChild(empty);
    }
    for (const table of tournamentData.active_tables) {
        tables.appendChild(tableButton(table));
    }

    const historyTitle = document.createElement('div');
    historyTitle.className = 'section-title';
    historyTitle.textContent = 'Архив';
    tables.appendChild(historyTitle);
    if (tournamentData.history_tables.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'muted';
        empty.textContent = 'Пока нет';
        tables.appendChild(empty);
    }
    for (const table of tournamentData.history_tables) {
        tables.appendChild(tableButton(table));
    }

    // Активные турниры: кнопка счёта и турниры, в которых я играю
    const running = document.getElementById('tournament-running');
    running.innerHTML = '';
    const scoreButton = document.getElementById('btn-tournament-score');

    if (tournamentData.running.length === 0) {
        scoreButton.classList.add('hidden');
        const empty = document.createElement('div');
        empty.className = 'empty';
        empty.textContent = 'Сейчас вы не играете ни в одном турнире';
        running.appendChild(empty);
    } else {
        scoreButton.classList.remove('hidden');
    }
    for (const tournament of tournamentData.running) {
        running.appendChild(runningCard(tournament));
    }
}

async function loadTournaments() {
    const result = await apiGet('/api/tournaments');
    if (result.status !== 200) {
        return;
    }
    tournamentData = result.data;
    fillTournaments();
}

function updateTournamentPrice() {
    const crystals = Number(document.getElementById('tournament-crystals').value || 0);
    const price = Math.round((selectedTournament.price - crystals / tournamentData.crystals_per_ruble) * 10) / 10;
    document.getElementById('tournament-price').textContent = price;
}

function openTournamentModal(tournament) {
    selectedTournament = tournament;

    document.getElementById('tournament-title').textContent = tournament.name;
    let details = tournamentDetails(tournament);
    if (tournament.status === 'can_register_second') {
        details += '\n➕ Запись ещё в один дивизион: ' + tournament.division_name;
    }
    document.getElementById('tournament-details').textContent = details;
    document.getElementById('tournament-details').className = 'tournament-details pay-path';
    document.getElementById('tournament-regulations').textContent = tournament.regulations || 'Регламент не указан';

    document.getElementById('tournament-step-rules').classList.remove('hidden');
    document.getElementById('tournament-step-pay').classList.add('hidden');
    document.getElementById('tournament-photo').value = '';
    document.getElementById('tournament-crystals').value = '';

    document.getElementById('tournament-modal').classList.remove('hidden');
}

function showPaymentStep() {
    const payment = tournamentData.payment;
    if (!payment) {
        tg.showAlert('Произошла ошибка загрузки страницы оплаты! Пожалуйста, свяжитесь с поддержкой бота');
        return;
    }

    document.getElementById('tournament-pay-path').textContent = '• Система «Расчёт» (ЕРИП)\n• Банковские, финансовые услуги\n• Банки, НКФО\n• ' + payment.bank + '\n• Пополнение счёта\n\nВведите номер счёта:';
    document.getElementById('tournament-account').textContent = payment.account;

    // Кристаллы
    const crystalsField = document.getElementById('tournament-crystals-field');
    if (tournamentData.can_use_crystals && tournamentData.crystals >= tournamentData.min_crystals) {
        document.getElementById('tournament-crystals-label').textContent = 'Применить кристаллы 💎 (у вас ' + tournamentData.crystals + ', мин. ' + tournamentData.min_crystals + ')';
        crystalsField.classList.remove('hidden');
    } else {
        crystalsField.classList.add('hidden');
    }

    updateTournamentPrice();
    document.getElementById('tournament-step-rules').classList.add('hidden');
    document.getElementById('tournament-step-pay').classList.remove('hidden');
}

async function sendPayment() {
    const photo = document.getElementById('tournament-photo').files[0];
    if (!photo) {
        tg.showAlert('Прикрепите скриншот чека об оплате');
        return;
    }

    // Фото отправляем формой (multipart), а не JSON
    const form = new FormData();
    form.append('tournament_id', selectedTournament.id);
    form.append('crystals', document.getElementById('tournament-crystals').value || '0');
    form.append('photo', photo);

    const button = document.getElementById('tournament-send');
    button.disabled = true;
    button.textContent = 'Отправляем...';

    let result;
    try {
        const response = await fetch('/api/tournaments/pay', {
            method: 'POST',
            headers: { 'X-Init-Data': tg.initData },
            body: form
        });
        result = { status: response.status, data: await response.json() };
    } catch (error) {
        result = { status: 0, data: { error: 'Не удалось отправить чек. Проверьте интернет и попробуйте ещё раз' } };
    }

    button.disabled = false;
    button.textContent = 'Отправить чек';

    if (handleError(result)) {
        return;
    }

    tg.HapticFeedback.notificationOccurred('success');
    document.getElementById('tournament-modal').classList.add('hidden');
    tg.showAlert('Спасибо за оплату! 😎 Редакторы уже проверяют чек — бот пришлёт сообщение, когда регистрацию подтвердят');
    await loadTournaments();
}

// Счёт турнирной игры
function fillTournamentOpponents() {
    const tournamentId = Number(document.getElementById('tscore-tournament').value);
    const select = document.getElementById('tscore-opponent');
    select.innerHTML = '';

    for (const tournament of tournamentData.running) {
        if (tournament.id !== tournamentId) {
            continue;
        }
        for (const player of tournament.players) {
            const option = document.createElement('option');
            option.value = player.id;
            option.textContent = player.name + ' (' + player.division + ')';
            select.appendChild(option);
        }
    }
}

function openTournamentScore() {
    if (!tournamentData || tournamentData.running.length === 0) {
        tg.showAlert('Записать счёт можно, когда идёт турнир, в котором вы участвуете');
        return;
    }

    const select = document.getElementById('tscore-tournament');
    select.innerHTML = '';
    for (const tournament of tournamentData.running) {
        const option = document.createElement('option');
        option.value = tournament.id;
        option.textContent = tournament.name;
        select.appendChild(option);
    }
    fillTournamentOpponents();

    // Поля для 3 сетов
    const sets = document.getElementById('tscore-sets');
    sets.innerHTML = '';
    for (let i = 1; i <= 3; i++) {
        const row = document.createElement('div');
        row.className = 'set-row';

        const label = document.createElement('span');
        label.className = 'muted';
        label.textContent = 'Сет ' + i;

        const mine = document.createElement('input');
        mine.type = 'number';
        mine.min = '0';
        mine.inputMode = 'numeric';

        const theirs = document.createElement('input');
        theirs.type = 'number';
        theirs.min = '0';
        theirs.inputMode = 'numeric';

        row.appendChild(label);
        row.appendChild(mine);
        row.appendChild(theirs);
        sets.appendChild(row);
    }

    document.getElementById('score-modal').classList.add('hidden');
    document.getElementById('tscore-modal').classList.remove('hidden');
}

async function sendTournamentScore() {
    const sets = [];
    const rows = document.querySelectorAll('#tscore-sets .set-row');
    for (const row of rows) {
        const inputs = row.querySelectorAll('input');
        if (inputs[0].value === '' && inputs[1].value === '') {
            continue;  // Пустой сет пропускаем
        }
        sets.push([Number(inputs[0].value), Number(inputs[1].value)]);
    }

    const body = {
        tournament_id: Number(document.getElementById('tscore-tournament').value),
        opponent_id: Number(document.getElementById('tscore-opponent').value),
        sets: sets
    };

    const button = document.getElementById('tscore-send');
    button.disabled = true;
    const result = await apiPost('/api/tournaments/score', body);
    button.disabled = false;

    if (handleError(result)) {
        return;
    }

    tg.HapticFeedback.notificationOccurred('success');
    document.getElementById('tscore-modal').classList.add('hidden');
    tg.showAlert('✅ Счёт отправлен сопернику на подтверждение');
}

function setupTournament() {
    const segments = document.querySelectorAll('#tournament-tabs .segment');
    for (const segment of segments) {
        segment.addEventListener('click', function () {
            for (const other of segments) {
                other.classList.remove('active');
                document.getElementById('tournament-' + other.dataset.tournament).classList.add('hidden');
            }
            segment.classList.add('active');
            document.getElementById('tournament-' + segment.dataset.tournament).classList.remove('hidden');
        });
    }

    document.getElementById('tournament-to-pay').addEventListener('click', showPaymentStep);
    document.getElementById('tournament-crystals').addEventListener('input', updateTournamentPrice);
    document.getElementById('tournament-send').addEventListener('click', sendPayment);
    document.getElementById('tournament-close').addEventListener('click', function () {
        document.getElementById('tournament-modal').classList.add('hidden');
    });
    document.getElementById('tournament-copy-account').addEventListener('click', async function () {
        try {
            await navigator.clipboard.writeText(tournamentData.payment.account);
            tg.showAlert('Номер счёта скопирован!');
        } catch (error) {
            tg.showAlert(tournamentData.payment.account);
        }
    });

    document.getElementById('btn-tournament-score').addEventListener('click', openTournamentScore);
    document.getElementById('score-tournament-btn').addEventListener('click', openTournamentScore);
    document.getElementById('tscore-tournament').addEventListener('change', fillTournamentOpponents);
    document.getElementById('tscore-send').addEventListener('click', sendTournamentScore);
    document.getElementById('tscore-close').addEventListener('click', function () {
        document.getElementById('tscore-modal').classList.add('hidden');
    });
}


// ---------- Соперник ----------

let courts = [];

function myId() {
    return tg.initDataUnsafe.user.id;
}

// Строка с игроком: имя (нажатие открывает чат с ним), дивизион и рейтинг
function playerRow(player) {
    const row = document.createElement('div');
    row.className = 'player-row';

    const name = document.createElement('button');
    name.className = 'player-name';
    name.type = 'button';
    name.textContent = '🙋‍♂️ ' + player.name;
    if (player.link) {
        name.addEventListener('click', function () {
            tg.openTelegramLink(player.link);
        });
    }

    const info = document.createElement('span');
    info.className = 'muted';
    info.textContent = player.division + (player.rating !== null ? ' ⚡️ ' + player.rating : '');

    row.appendChild(name);
    row.appendChild(info);
    return row;
}

function playerNames(card, ids) {
    const names = [];
    for (const player of card.players) {
        if (ids.includes(player.id)) {
            names.push(player.name);
        }
    }
    return names.join(', ');
}

// Статус игры для вкладки "Мои игры"
function gameStatus(card) {
    if (card.status === 'done') {
        let text = '✅ ' + playerNames(card, card.team_1) + ' ' + card.score + ' ' + playerNames(card, card.team_2);
        if (card.my_reward !== null) {
            text += ' · +' + card.my_reward + ' 🪙';
        }
        return text;
    }
    if (card.status === 'confirming') {
        return '⏳ Счёт ' + card.score + ' на подтверждении';
    }
    if (card.status === 'wait_score') {
        return '✍️ Ждём счёт — нажмите круглую кнопку слева';
    }
    if (card.players.length < card.places) {
        return '⏳ Ждём игроков (' + card.players.length + ' из ' + card.places + ')';
    }
    return '🎾 Игра впереди';
}

// Карточка игры. mode: search — можно откликнуться, request — моя заявка, game — моя игра
function matchCard(card, mode) {
    const box = document.createElement('div');
    box.className = 'card';

    const date = document.createElement('div');
    date.className = 'match-date';
    date.textContent = '⏰ ' + card.date;
    box.appendChild(date);

    const court = document.createElement('div');
    court.className = 'match-line';
    if (card.booked) {
        court.textContent = '✅ Корт забронирован: ' + card.court;
    } else {
        court.textContent = '❌ Корт не забронирован';
    }
    box.appendChild(court);

    const type = document.createElement('div');
    type.className = 'match-line';
    type.textContent = '🎾 ' + card.type + ' · игроков ' + card.players.length + ' из ' + card.places;
    box.appendChild(type);

    if (card.comment) {
        const comment = document.createElement('div');
        comment.className = 'match-comment';
        comment.textContent = card.comment;
        box.appendChild(comment);
    }

    for (const player of card.players) {
        box.appendChild(playerRow(player));
    }

    if (mode === 'search') {
        const button = document.createElement('button');
        button.className = 'btn btn-gold btn-wide';
        button.type = 'button';
        button.textContent = 'Откликнуться';
        button.addEventListener('click', async function () {
            button.disabled = true;
            const result = await apiPost('/api/matches/apply', { match_id: card.id });
            if (handleError(result)) {
                button.disabled = false;
                return;
            }
            tg.HapticFeedback.notificationOccurred('success');
            button.textContent = '✅ Заявка отправлена';
        });
        box.appendChild(button);
    }

    if (mode === 'request') {
        const button = document.createElement('button');
        button.className = 'btn btn-red btn-wide';
        button.type = 'button';
        button.textContent = 'Удалить заявку';
        button.addEventListener('click', function () {
            tg.showConfirm('Удалить заявку на ' + card.date + '?', async function (ok) {
                if (!ok) {
                    return;
                }
                const result = await apiPost('/api/matches/delete', { match_id: card.id });
                if (!handleError(result)) {
                    loadOpponent();
                }
            });
        });
        box.appendChild(button);
    }

    if (mode === 'game') {
        const status = document.createElement('div');
        status.className = 'status';
        status.textContent = gameStatus(card);
        box.appendChild(status);
    }

    return box;
}

function fillList(containerId, cards, mode, emptyText) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    if (cards.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'empty';
        empty.textContent = emptyText;
        container.appendChild(empty);
        return;
    }

    for (const card of cards) {
        container.appendChild(matchCard(card, mode));
    }
}

async function loadOpponent() {
    const search = await apiGet('/api/matches/search');
    const mine = await apiGet('/api/matches/mine');

    fillList('opponent-search', search.data, 'search', 'Пока никто не ищет соперника. Создайте свою заявку! 🎾');
    fillList('opponent-requests', mine.data.requests, 'request', 'У вас нет открытых заявок');
    fillList('opponent-games', mine.data.games, 'game', 'Здесь появятся игры, в которых собран состав');

    courts = mine.data.courts;
}

function setupOpponent() {
    const segments = document.querySelectorAll('#opponent-tabs .segment');
    for (const segment of segments) {
        segment.addEventListener('click', function () {
            for (const other of segments) {
                other.classList.remove('active');
                document.getElementById('opponent-' + other.dataset.opponent).classList.add('hidden');
            }
            segment.classList.add('active');
            document.getElementById('opponent-' + segment.dataset.opponent).classList.remove('hidden');
        });
    }

    document.getElementById('btn-create-match').addEventListener('click', openCreateModal);
    document.getElementById('create-cancel').addEventListener('click', function () {
        document.getElementById('create-modal').classList.add('hidden');
    });
    document.getElementById('create-submit').addEventListener('click', submitCreate);
}

function openCreateModal() {
    // Список кортов
    const select = document.getElementById('create-court');
    select.innerHTML = '';

    const noCourt = document.createElement('option');
    noCourt.value = '';
    noCourt.textContent = 'Корт не забронирован';
    select.appendChild(noCourt);

    for (const court of courts) {
        const option = document.createElement('option');
        option.value = court;
        option.textContent = court;
        select.appendChild(option);
    }

    // Возраст и пол спрашиваем, только если их ещё нет в профиле
    if (profile.age) {
        document.getElementById('create-age-field').classList.add('hidden');
    } else {
        document.getElementById('create-age-field').classList.remove('hidden');
    }
    if (profile.sex) {
        document.getElementById('create-sex-field').classList.add('hidden');
    } else {
        document.getElementById('create-sex-field').classList.remove('hidden');
    }

    document.getElementById('create-modal').classList.remove('hidden');
}

async function submitCreate() {
    const court = document.getElementById('create-court').value;

    const body = {
        type: document.getElementById('create-type').value,
        booked: court !== '',
        court: court,
        date: document.getElementById('create-date').value,
        comment: document.getElementById('create-comment').value,
        age: document.getElementById('create-age').value,
        sex: document.getElementById('create-sex').value
    };

    const button = document.getElementById('create-submit');
    button.disabled = true;
    const result = await apiPost('/api/matches/create', body);
    button.disabled = false;

    if (handleError(result)) {
        return;
    }

    tg.HapticFeedback.notificationOccurred('success');
    document.getElementById('create-modal').classList.add('hidden');
    document.getElementById('create-comment').value = '';

    // Возраст и пол сохранились — больше не спрашиваем
    if (body.age) {
        profile.age = body.age;
    }
    if (body.sex) {
        profile.sex = body.sex;
    }

    await loadOpponent();
    document.querySelector('#opponent-tabs .segment[data-opponent=requests]').click();
    tg.showAlert('✅ Заявка создана! Когда кто-то откликнется, бот пришлёт вам сообщение');
}


// ---------- Счёт ----------

let pendingGames = [];

async function loadPending() {
    const result = await apiGet('/api/score/pending');
    pendingGames = result.data;

    const badge = document.getElementById('score-badge');
    if (pendingGames.length > 0) {
        badge.textContent = pendingGames.length;
        badge.classList.remove('hidden');
    } else {
        badge.classList.add('hidden');
    }
}

function openScoreModal() {
    const list = document.getElementById('score-list');
    list.innerHTML = '';

    if (pendingGames.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'empty';
        empty.textContent = 'Нет матчей для выставления счёта';
        list.appendChild(empty);
    }

    for (const card of pendingGames) {
        list.appendChild(scoreForm(card));
    }

    document.getElementById('score-modal').classList.remove('hidden');
}

// Форма счёта для одной игры
function scoreForm(card) {
    const box = document.createElement('div');
    box.className = 'card score-game';

    const date = document.createElement('div');
    date.className = 'match-date';
    date.textContent = '⏰ ' + card.date + ' · ' + card.type;
    box.appendChild(date);

    // Остальные игроки
    const others = [];
    for (const player of card.players) {
        if (player.id !== myId()) {
            others.push(player);
        }
    }

    // В парной игре выбираем партнёра — остальные двое станут соперниками
    let partnerSelect = null;
    if (card.type === 'Парный') {
        const field = document.createElement('label');
        field.className = 'field';

        const label = document.createElement('span');
        label.textContent = 'Мой партнёр по команде';
        field.appendChild(label);

        partnerSelect = document.createElement('select');
        for (const player of others) {
            const option = document.createElement('option');
            option.value = player.id;
            option.textContent = player.name;
            partnerSelect.appendChild(option);
        }
        field.appendChild(partnerSelect);
        box.appendChild(field);
    } else {
        const line = document.createElement('div');
        line.className = 'match-line';
        line.textContent = 'Соперник: ' + others[0].name;
        box.appendChild(line);
    }

    // Сеты: левый столбик — моя команда, правый — соперники
    const header = document.createElement('div');
    header.className = 'sets-header';
    header.innerHTML = '<span></span><span>Мы</span><span>Соперники</span>';
    box.appendChild(header);

    const inputs = [];
    for (let i = 1; i <= 3; i++) {
        const row = document.createElement('div');
        row.className = 'set-row';

        const label = document.createElement('span');
        label.className = 'muted';
        label.textContent = 'Сет ' + i;

        const mine = document.createElement('input');
        mine.type = 'number';
        mine.min = '0';
        mine.inputMode = 'numeric';

        const theirs = document.createElement('input');
        theirs.type = 'number';
        theirs.min = '0';
        theirs.inputMode = 'numeric';

        row.appendChild(label);
        row.appendChild(mine);
        row.appendChild(theirs);
        box.appendChild(row);

        inputs.push([mine, theirs]);
    }

    const hint = document.createElement('div');
    hint.className = 'muted';
    hint.textContent = 'Третий сет оставьте пустым, если играли два';
    box.appendChild(hint);

    const button = document.createElement('button');
    button.className = 'btn btn-gold btn-wide';
    button.type = 'button';
    button.textContent = 'Отправить на подтверждение';
    button.addEventListener('click', async function () {
        const sets = [];
        for (const pair of inputs) {
            if (pair[0].value === '' && pair[1].value === '') {
                continue;  // Пустой сет пропускаем
            }
            sets.push([Number(pair[0].value), Number(pair[1].value)]);
        }

        const body = { match_id: card.id, sets: sets };
        if (partnerSelect) {
            body.partner_id = Number(partnerSelect.value);
        }

        button.disabled = true;
        const result = await apiPost('/api/score/submit', body);
        button.disabled = false;

        if (handleError(result)) {
            return;
        }

        tg.HapticFeedback.notificationOccurred('success');
        tg.showAlert('✅ Счёт отправлен на подтверждение. Монеты придут, когда все подтвердят');
        await loadPending();
        await loadOpponent();
        openScoreModal();
    });
    box.appendChild(button);

    return box;
}

function setupScore() {
    document.getElementById('score-fab').addEventListener('click', async function () {
        tg.HapticFeedback.selectionChanged();
        await loadPending();
        openScoreModal();
    });

    document.getElementById('score-close').addEventListener('click', function () {
        document.getElementById('score-modal').classList.add('hidden');
    });
}

// Открытие нужного экрана по ссылке из сообщения бота (?screen=score / opponent / arena)
function openFromLink() {
    const screen = new URLSearchParams(window.location.search).get('screen');

    if (screen === 'score') {
        openScoreModal();
    } else if (screen === 'opponent' || screen === 'arena' || screen === 'tournament') {
        showScreen(screen);
    }
}


// ---------- Остальные экраны ----------

function setupBooking() {
    document.getElementById('btn-booking').addEventListener('click', function () {
        tg.openTelegramLink('https://t.me/mw_tennis_bot');
    });
}

function setupShop() {
    const segments = document.querySelectorAll('#screen-shop .segment');
    for (const segment of segments) {
        segment.addEventListener('click', function () {
            for (const other of segments) {
                other.classList.remove('active');
            }
            segment.classList.add('active');

            if (segment.dataset.shop === 'skins') {
                document.getElementById('shop-skins').classList.remove('hidden');
                document.getElementById('shop-market').classList.add('hidden');
            } else {
                document.getElementById('shop-skins').classList.add('hidden');
                document.getElementById('shop-market').classList.remove('hidden');
            }
        });
    }
}

function showError(title, text) {
    document.getElementById('topbar-name').textContent = '';
    document.getElementById('error-title').textContent = title;
    document.getElementById('error-text').textContent = text;
    showScreen('error');
    document.querySelector('.tabbar').classList.add('hidden');
    document.getElementById('score-fab').classList.add('hidden');
    document.getElementById('daily-fab').classList.add('hidden');
    document.getElementById('news-btn').classList.add('hidden');
}


// ---------- Запуск ----------

async function start() {
    setupNavigation();
    setupReferralButtons();
    setupBooking();
    setupShop();
    setupOpponent();
    setupScore();
    setupTournament();

    if (!tg.initData) {
        showError('Откройте приложение в Telegram', 'Приложение работает только внутри Telegram — нажмите кнопку «Приложение» в боте');
        return;
    }

    try {
        const result = await apiGet('/api/me');

        if (result.status === 404) {
            showError('Вы ещё не зарегистрированы', 'Отправьте боту команду /start и пройдите регистрацию');
            return;
        }
        if (result.status !== 200) {
            showError('Не удалось загрузить профиль', 'Закройте и откройте приложение ещё раз');
            return;
        }

        profile = result.data;
        fillProfile();
        fillLeague();
        fillDaily();
        fillNewsDot();

        const history = await apiGet('/api/gold_history');
        fillHistory(history.data);

        await loadOpponent();
        await loadPending();
        await loadTournaments();
        showScreen('arena');  // Приложение открывается на главном экране

        // Итоги прошлого года (если есть) и экран из ссылки бота
        showSeasonSummary();
        openFromLink();
    } catch (error) {
        showError('Нет связи с сервером', 'Проверьте интернет и попробуйте ещё раз');
    }
}

start();
