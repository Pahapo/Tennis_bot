const tg = window.Telegram.WebApp;

tg.ready();   // Сообщаем Telegram, что приложение загрузилось
tg.expand();  // Раскрываем приложение на весь экран
tg.setHeaderColor('#0d1730');
tg.setBackgroundColor('#14213d');

// Названия локаций (лиг). Картинки лежат в /static/img/locations/1.svg ... 10.svg
const LOCATIONS = [
    'Дворовый корт',
    'Школьная площадка',
    'Парковый корт',
    'Грунтовый клуб',
    'Городская арена',
    'Травяной клуб',
    'Ночной стадион',
    'Крытый дворец',
    'Арена чемпионов',
    'Центральный корт'
];

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

function fillLocations() {
    const container = document.getElementById('locations');
    container.innerHTML = '';

    // Пока открыта только первая лига — прогресс появится на шаге "Лиги"
    for (let i = 0; i < LOCATIONS.length; i++) {
        const number = i + 1;
        const locked = number > 1;

        const card = document.createElement('div');
        card.className = 'location';
        if (locked) {
            card.classList.add('locked');
        }

        const picture = document.createElement('img');
        picture.className = 'location-picture';
        picture.src = '/static/img/locations/' + number + '.svg';
        picture.alt = LOCATIONS[i];
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
        name.textContent = number + '. ' + LOCATIONS[i];
        card.appendChild(name);

        container.appendChild(card);
    }
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
    fillLocations();

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
        showScreen('profile');
        tg.BackButton.hide();  // При первом открытии "Назад" не нужен
    } catch (error) {
        showError('Нет связи с сервером', 'Проверьте интернет и попробуйте ещё раз');
    }
}

start();
