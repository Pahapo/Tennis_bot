const tg = window.Telegram.WebApp;

tg.ready();   // Сообщаем Telegram, что приложение загрузилось
tg.expand();  // Раскрываем приложение на весь экран
tg.setHeaderColor('#0d1730');
tg.setBackgroundColor('#14213d');

let currentScreen = 'profile';
let previousScreen = 'arena';  // Куда вернуться из профиля по кнопке "Назад"
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

// POST-запрос к API бота
async function apiPost(url) {
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'X-Init-Data': tg.initData }
    });
    const data = await response.json();
    return { status: response.status, data: data };
}


// ---------- Навигация ----------

function showScreen(name) {
    if (name === 'profile' && currentScreen !== 'profile') {
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

    // Аватар подсвечен, когда открыт профиль
    const avatarButton = document.getElementById('avatar-btn');
    if (name === 'profile') {
        avatarButton.classList.add('active');
        tg.BackButton.show();
    } else {
        avatarButton.classList.remove('active');
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


// ---------- Остальные экраны ----------

function setupBooking() {
    document.getElementById('btn-booking').addEventListener('click', function () {
        tg.openTelegramLink('https://t.me/mw_tennis_bot');
    });
}

function setupShop() {
    const segments = document.querySelectorAll('.segment');
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
}


// ---------- Запуск ----------

async function start() {
    setupNavigation();
    setupReferralButtons();
    setupBooking();
    setupShop();

    if (!tg.initData) {
        showError('Откройте приложение в Telegram', 'Приложение работает только внутри Telegram — нажмите кнопку «Приложение» в боте');
        return;
    }

    try {
        const visit = await apiPost('/api/visit');  // Ежедневная награда и серия (сервер выдаёт её 1 раз в день)
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

        const history = await apiGet('/api/gold_history');
        fillHistory(history.data);
        showScreen('profile');
        tg.BackButton.hide();  // При первом открытии "Назад" не нужен

        // Сначала ежедневная награда, потом итоги прошлого года (если есть)
        showReward(visit.data, showSeasonSummary);
    } catch (error) {
        showError('Нет связи с сервером', 'Проверьте интернет и попробуйте ещё раз');
    }
}

start();
