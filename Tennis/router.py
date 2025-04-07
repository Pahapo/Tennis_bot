from aiogram import Router
from handlers.check_subscription import router as check_subscription
from handlers.contestant import router as contestant
from handlers.court_reservation import router as court_reservation
from handlers.functions import router as functions
from handlers.inventory import router as inventory
from handlers.registration_card import router as registration_card
from handlers.send_messages import router as send_messages
from handlers.start import router as start
from handlers.tournament import router as tournament
from handlers.registration_tournament import router as registration_tournament
from handlers.tournament_table import router as tournament_table
from handlers.create_tournament import router as create_tournament
from handlers.output_tournaments import router as output_tournaments
from handlers.btn_tournaments import router as btn_tournaments
from handlers.set_division import router as set_division

router = Router()


# Включаем все роутеры
router.include_router(check_subscription)
router.include_router(contestant)
router.include_router(court_reservation)
router.include_router(functions)
router.include_router(inventory)
router.include_router(registration_card)
router.include_router(send_messages)
router.include_router(start)
router.include_router(tournament)
router.include_router(registration_tournament)
router.include_router(tournament_table)
router.include_router(create_tournament)
router.include_router(output_tournaments)
router.include_router(btn_tournaments)
router.include_router(set_division)