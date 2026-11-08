V_0.5.0 {
global:
xkb_state_update_mask;
xkb_keymap_new_from_string;
xkb_compose_state_reset;
xkb_state_unref;
xkb_state_new;
xkb_keymap_mod_get_index;
xkb_compose_state_new;
xkb_state_key_get_one_sym;
xkb_compose_state_get_status;
xkb_compose_state_get_utf8;
xkb_state_serialize_mods;
xkb_compose_state_unref;
xkb_compose_table_unref;
xkb_context_unref;
xkb_context_new;
xkb_compose_table_new_from_locale;
xkb_compose_state_feed;
xkb_state_key_get_utf8;
xkb_state_get_keymap;
xkb_keymap_key_repeats;
xkb_keymap_unref;
local: *;
};
