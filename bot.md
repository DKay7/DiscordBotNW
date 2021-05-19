# Модерация
## Команды: 
 - `++` `/kick`, 
 - `++` `/ban` -> в лс отправить, 
 - `++` `/unban`, 
 - `++` `/tempban` (участник, время, причины) -> при бане пишет участнику сообщение. 
 - `++` `/mute` (игрок, причина, время, каналы[текстовые, голосовые, везде]) -> в лс отправляет
 - `++` `/unmute`
 - `++` `/warn` (участник, причина) -> лс участнику с предупреждением и причиной -> 3 предупреждении = бан на сутки.
 - `++` `/unwarn` (участник, причина) -> удаление warn
 - `++` `/temp_role`

---

# Кланы

1. `++`  Кто-то запускает команду, например, \choose_leader @username
2. `++` Пользователю @username приходит сообщение в дм, с двумя реакциями: согласиться/отказаться
3. `++`  Если он отказывается, в общий чат сообщается, что он отказался, больше ничего не происходит
4. Если он согласился, то:

        `++` 4.1. Ему предлагают выбрать название клана
        `++` 4.2. Создаются три роли: лидер клана, зам. лидера, участник клана
        `++` 4.3 Роль лидера назначается @username
        `++` 4.4. Создаются три клановых канала: Чат клана, рейтинг клана, голосовой канал клана
        `++` 4.5. Лидеру открывается доступ к текстовым каналам: клановый чат, войны, общий рейтинг.

 `++` - роли: лидер + зам + участник

 `++` - Клановый лидер может повысить участника до зама. Команда `choose_dep`
 
 `--` - Лидер и зам могут пригласить участников в клан. Команда `invite`

 `--` - Команда `win` начисляет одно победное очко клану в бд.
 
 `--` - Комадна `top_clan` показывает топ-10 кланов по количеству очков побед

---

# Рейтинг пользователей
- `++`  Общение в текстовом канале -> опыт. Не за каждое сообщение. за каждые 5 сообщений единица опыта. (все каналы, кроме спама). Сделать проверку на отсутствие команд в сообщении.
- `++`  Голосовой канал. Каждый полчаса всем начисляется единица опыта.
- `++`  Определенное количество очков повышает уровень. Каждый уровень количество очков увеличивается в 2 раза.
- `++`  Каждые 5 уровней выдается роль. Сделать массив ролей.
- `++`  Когда пользователь достигает нового уровня, ему в лс отправляется уведомление. "Вам была выдана такая-то роль, потому что вы достигли такого-то уровня".
- Команда \rank. Выводит сообщение с прогресс-баром до следующего уровня.

---

# Утилиты
- \avatar. Отправляет аватар переданного пользователя.

- Команды взаимодействея. Все команды работают по принципу отправки сообщения вида @пользователь1 <действие> [@пользователь2]
- - \kiss
- - \hug
- - \highfive
- - \pat
- - \cry
- - \suicide
- - \poke
- - \punch
- - \dance
- - \wokeup
- - \punch
- - \dodge
- - \wokeup
- - \nom
- - \sex
- - \welcome
- - \marrige -> предлагает пользователю жениться/выйти замуж за переданного пользователя. 
        В случае согласия, в бд добавляется информация о муже/жене пользователя.

- \serverinfo Выводит информацию о сервере, как на картинке
- \userinfo Выводит информацию о пользователе, как на картинке

---

# АвтоМодерация
удалять везде, кроме спам-канала:
- ссылки (ютуб-ссылки), удалить ссылку и выслать сообщение с предупреждением
- плохие слова
- удаляет похожие сообщения, если их больше 6. Похожесть -- считать косинусную меру. После 6 удалять все, кроме первого, высылать предупреждение
- То же с сообщением в верхнем регистре. Больше 3 сообщений -- удалять все, кроме одного. Высылать предупреждение.
- То же со смайликами. Больше 3 сообщений со смайликом -- удалять все, кроме одного. Высылать предупреждение.
- То же с упоминанием. Больше 3 сообщений со смайликом -- удалять все, кроме одного. Высылать предупреждение.

---

# Рейтинг пользователя внутри клана
- Для каждого клана создается канал "рейтинг клана". У каждого клана свой рейтинг (хранить в бд уникальный ключ как связку id пользователя и id группы клановых каналов).
- Клановый рейтинг пользователь зарабатывает в текстовом/головосом канале клана. Как в обычном рейтинге. Каждые n-очков выдается уровень. Каждые m-уровней получается роль. **При этом обычный рейтинг не начисляется.** (при создании группы клановых каналов, добавлять id группы в список запрещенных групп для обычного рейтинга)

- При повышении уровня отправляется не в лс, а в канал "рейтинг клана".
- Команда для рейтинга внутри клана. С картинкой.