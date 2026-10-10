
from unittest.mock import patch, MagicMock

from app.services.translation_service import translate_text


def test_translate_text_returns_english_translation():
    with patch(
        "app.services.translation_service.client.models.generate_content"
    ) as mock_generate:
        mock_generate.return_value = MagicMock(
            text="Why did I come here for this fight?"
        )

        result = translate_text(
            "ఓ వీడితో ఎందుకు వచ్చాను గొడవ ఎంతో కొంత",
            "Telugu",
        )

        assert result == "Why did I come here for this fight?"
        mock_generate.assert_called_once()


def test_translate_text_translates_telugu_text():
    telugu_text = "వేస్తే బెటర్"
    expected_translation = "It would be better to do that."

    with patch(
        "app.services.translation_service.client.models.generate_content"
    ) as mock_generate:
        mock_generate.return_value = MagicMock(
            text=expected_translation
        )

        result = translate_text(telugu_text, "Telugu")

        assert result == expected_translation

        # Verify the actual prompt includes the original text and language.
        prompt = mock_generate.call_args.kwargs["contents"]
        assert telugu_text in prompt
        assert "Telugu" in prompt
