from aiogram import Router
from handlers.check_subscription import router as check_subscription
from handlers.match import router as match
from handlers.court_reservation import router as court_reservation
from handlers.functions import router as functions
from handlers.inventory import router as inventory
from handlers.registration_card import router as registration_card
from handlers.send_messages import router as send_messages
from handlers.start import router as start
from handlers.tournament import router as tournament
from handlers.payment import router as payment
from handlers.tournament_table import router as tournament_table
from handlers.create_tournament import router as create_tournament
from handlers.output_tournaments import router as output_tournaments
from handlers.btn_tournaments import router as btn_tournaments
from handlers.set_ban import router as set_ban
from handlers.set_division import router as set_division
from handlers.delete_players import router as delete_players
from handlers.delete_tournament import router as delete_tournament
from handlers.edit_tournament import router as edit_tournament
from handlers.output_player_without_division import router as output_player_without_division
from handlers.booking_court import router as booking_court
from handlers.referrals import router as referrals
from handlers.kassa import router as kassa
from handlers.score import router as score
from handlers.rename_user import router as rename_user
from handlers.about_me import router as about_me
from handlers.match_app import router as match_app
from handlers.tournament_app import router as tournament_app
# from handlers.create_chats import router as create_chats


router = Router()


# Включаем все роутеры
router.include_router(check_subscription)
router.include_router(match)
router.include_router(court_reservation)
router.include_router(functions)
router.include_router(inventory)
router.include_router(registration_card)
router.include_router(send_messages)
router.include_router(start)
router.include_router(tournament)
router.include_router(payment)
router.include_router(tournament_table)
router.include_router(create_tournament)
router.include_router(output_tournaments)
router.include_router(btn_tournaments)
router.include_router(set_ban)
router.include_router(set_division)
router.include_router(delete_players)
router.include_router(delete_tournament)
router.include_router(edit_tournament)
router.include_router(output_player_without_division)
router.include_router(booking_court)
router.include_router(referrals)
router.include_router(kassa)
router.include_router(score)
router.include_router(rename_user)
router.include_router(about_me)
router.include_router(match_app)
router.include_router(tournament_app)
# router.include_router(create_chats)