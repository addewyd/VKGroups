.PHONY: po mo

po:
	xgettext -Lpython --output=messages.pot program.py libs/utils/showplugins.py libs/utils/authorization.py libs/uix/kv/license.kv libs/uix/kv/navdrawer.kv libs/uix/kv/startscreen.kv libs/uix/kv/comment.kv libs/uix/kv/list_user_groups.kv libs/uix/kv/navbutton.kv libs/uix/kv/passwordform.kv
	msgmerge --update --no-fuzzy-matching --backup=off data/locales/po/ru.po messages.pot
	msgmerge --update --no-fuzzy-matching --backup=off data/locales/po/en.po messages.pot

mo:
	mkdir -p data/locales/ru/LC_MESSAGES
	mkdir -p data/locales/en/LC_MESSAGES
	msgfmt -c -o data/locales/ru/LC_MESSAGES/kivyissues.mo data/locales/po/ru.po
	msgfmt -c -o data/locales/en/LC_MESSAGES/kivyissues.mo data/locales/po/en.po
