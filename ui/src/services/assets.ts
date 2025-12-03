// ui/src/services/assets.ts

const ASSET_BASE = '/assets';

export const WorkmateAssets = {
  workmateDark: `${ASSET_BASE}/workmate_dark_transparent.png`,
  workmateWhite: `${ASSET_BASE}/workmate_white_transparent.png`,
  workmateFavicon: `${ASSET_BASE}/workmate_favicon.ico`,
  kitGrey: `${ASSET_BASE}/KIT_IT_GREY_NO_BACKGROUND.png`,
} as const;

// Debug in Development
if (import.meta.env.DEV) {
  console.log('🎨 WorkmateOS Assets:', WorkmateAssets);
}
