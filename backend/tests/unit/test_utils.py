"""
Unit tests for utility functions (lightning address normalization, keyboard converter,
secure logging, and waitlist promotion).
"""
import pytest

from meetups.views.auth import LightningServiceError, normalize_lightning_address


class TestNormalizeLightningAddress:

    def test_valid_address_returned_unchanged(self):
        assert normalize_lightning_address('alice@coinos.io') == 'alice@coinos.io'

    def test_leading_at_sign_stripped(self):
        assert normalize_lightning_address('@alice@coinos.io') == 'alice@coinos.io'

    def test_domain_lowercased(self):
        assert normalize_lightning_address('alice@COINOS.IO') == 'alice@coinos.io'

    def test_surrounding_whitespace_stripped(self):
        assert normalize_lightning_address('  alice@coinos.io  ') == 'alice@coinos.io'

    def test_empty_string_raises(self):
        with pytest.raises(LightningServiceError, match='입력해주세요'):
            normalize_lightning_address('')

    def test_whitespace_only_raises(self):
        with pytest.raises(LightningServiceError):
            normalize_lightning_address('   ')

    def test_missing_at_sign_raises(self):
        with pytest.raises(LightningServiceError, match='형식'):
            normalize_lightning_address('invalidaddress')

    def test_multiple_at_signs_raises(self):
        with pytest.raises(LightningServiceError, match='형식'):
            normalize_lightning_address('a@b@c.io')

    def test_space_in_username_raises(self):
        with pytest.raises(LightningServiceError, match='사용자명'):
            normalize_lightning_address('ali ce@coinos.io')

    def test_single_label_domain_raises(self):
        with pytest.raises(LightningServiceError, match='도메인'):
            normalize_lightning_address('alice@localhost')

    def test_username_with_dots_and_plus_valid(self):
        result = normalize_lightning_address('alice.bob+tag@coinos.io')
        assert result == 'alice.bob+tag@coinos.io'

    def test_subdomain_valid(self):
        result = normalize_lightning_address('user@sub.domain.com')
        assert result == 'user@sub.domain.com'

    def test_none_equivalent_empty_raises(self):
        with pytest.raises((LightningServiceError, AttributeError)):
            normalize_lightning_address(None)


class TestKeyboardConverter:

    def test_has_korean_characters_korean_string(self):
        from meetups.utils.keyboard_converter import has_korean_characters
        assert has_korean_characters('안녕') is True

    def test_has_korean_characters_english_string(self):
        from meetups.utils.keyboard_converter import has_korean_characters
        assert has_korean_characters('hello') is False

    def test_has_korean_characters_mixed_string(self):
        from meetups.utils.keyboard_converter import has_korean_characters
        assert has_korean_characters('hello안녕') is True

    def test_has_korean_characters_empty_string(self):
        from meetups.utils.keyboard_converter import has_korean_characters
        assert has_korean_characters('') is False

    def test_has_korean_characters_numbers_only(self):
        from meetups.utils.keyboard_converter import has_korean_characters
        assert has_korean_characters('12345') is False

    def test_korean_to_english_returns_string(self):
        from meetups.utils.keyboard_converter import korean_to_english
        result = korean_to_english('ㅗㅔㅣㅣㅐ')
        assert isinstance(result, str)
        assert len(result) > 0

    def test_korean_to_english_full_syllable(self):
        from meetups.utils.keyboard_converter import korean_to_english
        # '안' is a full Korean syllable — triggers decompose_korean_char
        result = korean_to_english('안')
        assert isinstance(result, str)
        assert len(result) > 0

    def test_korean_to_english_mixed_ascii_and_korean(self):
        from meetups.utils.keyboard_converter import korean_to_english
        result = korean_to_english('hello안녕')
        assert 'hello' in result
        assert isinstance(result, str)

    def test_korean_to_english_ascii_passthrough(self):
        from meetups.utils.keyboard_converter import korean_to_english
        assert korean_to_english('abc123') == 'abc123'

    def test_decompose_korean_char_full_syllable(self):
        from meetups.utils.keyboard_converter import decompose_korean_char
        result = decompose_korean_char('한')
        assert isinstance(result, str)
        assert len(result) > 0

    def test_decompose_korean_char_non_korean_passthrough(self):
        from meetups.utils.keyboard_converter import decompose_korean_char
        assert decompose_korean_char('a') == 'a'
        assert decompose_korean_char('1') == '1'

    def test_decompose_korean_char_with_final_consonant(self):
        from meetups.utils.keyboard_converter import decompose_korean_char
        # '국' has initial ㄱ, medial ㅜ, final ㄱ
        result = decompose_korean_char('국')
        assert isinstance(result, str)
        assert len(result) >= 2

    def test_has_korean_characters_hangul_jamo_range(self):
        from meetups.utils.keyboard_converter import has_korean_characters
        # ㄱ is in Hangul Compatibility Jamo range (0x3130-0x318F)
        assert has_korean_characters('ㄱ') is True

    def test_korean_to_english_special_chars_passthrough(self):
        from meetups.utils.keyboard_converter import korean_to_english
        result = korean_to_english('!@#$%')
        assert result == '!@#$%'


@pytest.mark.django_db
class TestPromoteFromWaitlist:

    def test_promotes_first_waitlisted_user(self, create_meetup, create_meetup_user):
        from meetups.models import Registration, Waitlist
        from meetups.utils import promote_from_waitlist

        meetup = create_meetup(max_participants=2)
        # Fill the meetup
        u1 = create_meetup_user(name='U1', email='u1@promo.com')
        u2 = create_meetup_user(name='U2', email='u2@promo.com')
        Registration.objects.create(user=u1, meetup=meetup)
        Registration.objects.create(user=u2, meetup=meetup)

        # Add waitlisted user
        waiter = create_meetup_user(name='Waiter', email='waiter@promo.com')
        Waitlist.objects.create(user=waiter, meetup=meetup)

        # Free a spot
        reg = Registration.objects.get(user=u1, meetup=meetup)
        # Bypass model's delete() so we can manually test promote_from_waitlist
        from meetups.models import Registration as R
        R.objects.filter(id=reg.id).delete()
        meetup.current_participants = 1
        meetup.save()

        result = promote_from_waitlist(meetup)
        assert result is not None
        assert Registration.objects.filter(user=waiter, meetup=meetup).exists()
        assert not Waitlist.objects.filter(user=waiter, meetup=meetup).exists()

    def test_returns_none_when_no_waitlist(self, create_meetup):
        from meetups.utils import promote_from_waitlist

        meetup = create_meetup(max_participants=5)
        result = promote_from_waitlist(meetup)
        assert result is None

    def test_returns_none_when_meetup_full(self, create_meetup, create_meetup_user):
        from meetups.models import Registration, Waitlist
        from meetups.utils import promote_from_waitlist

        meetup = create_meetup(max_participants=1)
        u1 = create_meetup_user(name='Full1', email='full1@promo.com')
        Registration.objects.create(user=u1, meetup=meetup)

        waiter = create_meetup_user(name='WaiterFull', email='waiterfull@promo.com')
        Waitlist.objects.create(user=waiter, meetup=meetup)

        result = promote_from_waitlist(meetup)
        assert result is None

    def test_creates_notification_on_promotion(self, create_meetup, create_meetup_user):
        from meetups.models import Notification, Registration, Waitlist
        from meetups.utils import promote_from_waitlist

        meetup = create_meetup(max_participants=2)
        u1 = create_meetup_user(name='Slot1', email='slot1@promo.com')
        Registration.objects.create(user=u1, meetup=meetup)

        waiter = create_meetup_user(name='WaiterNotif', email='waiternotif@promo.com')
        Waitlist.objects.create(user=waiter, meetup=meetup)

        promote_from_waitlist(meetup)
        assert Notification.objects.filter(user=waiter, meetup=meetup).exists()


class TestSecureLogging:

    def test_log_korean_conversion_in_debug_mode(self, settings):
        from meetups.utils.secure_logging import log_korean_conversion
        settings.DEBUG = True
        # Should not raise; logging path exercised
        log_korean_conversion('testuser', action='login')

    def test_log_korean_conversion_non_debug_no_error(self, settings):
        from meetups.utils.secure_logging import log_korean_conversion
        settings.DEBUG = False
        log_korean_conversion('testuser', action='registration')

    def test_log_authentication_attempt_success_debug(self, settings):
        from meetups.utils.secure_logging import log_authentication_attempt
        settings.DEBUG = True
        log_authentication_attempt('testuser', success=True, method='standard')

    def test_log_authentication_attempt_failure_debug(self, settings):
        from meetups.utils.secure_logging import log_authentication_attempt
        settings.DEBUG = True
        log_authentication_attempt('testuser', success=False, method='korean_converted')

    def test_log_authentication_attempt_non_debug(self, settings):
        from meetups.utils.secure_logging import log_authentication_attempt
        settings.DEBUG = False
        log_authentication_attempt('testuser', success=True)

    def test_secure_log_debug_mode(self, settings):
        from meetups.utils.secure_logging import secure_log
        settings.DEBUG = True
        secure_log('test message', level='info')

    def test_secure_log_production_explicit(self, settings):
        from meetups.utils.secure_logging import secure_log
        settings.DEBUG = False
        secure_log('prod message', level='warning', include_in_production=True)

    def test_secure_log_production_suppressed(self, settings):
        from meetups.utils.secure_logging import secure_log
        settings.DEBUG = False
        # Should not raise even though suppressed
        secure_log('suppressed', level='info', include_in_production=False)

    def test_get_setting_missing_attribute_returns_default(self):
        from meetups.utils.secure_logging import _get_setting
        result = _get_setting('NONEXISTENT_SETTING_XYZ', default='fallback')
        assert result == 'fallback'
