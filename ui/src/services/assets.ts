// ui/src/services/assets.ts

export const WorkmateAssets = {
  workmateDark: new URL(
    "@root-assets/workmate_dark_transparent.png",
    import.meta.url
  ).href,
  workmateWhite: new URL(
    "@root-assets/workmate_white_transparent.png",
    import.meta.url
  ).href,
  workmateFavicon: new URL("@root-assets/workmate_favicon.ico", import.meta.url)
    .href,
  kitGrey: new URL(
    "@root-assets/KIT_IT_GREY_NO_BACKGROUND.png",
    import.meta.url
  ).href,
};
