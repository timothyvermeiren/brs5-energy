import type { Locale } from "../types.js";
import { formatDistance } from "./_lib/formatDistance/index.js";
import { formatLong } from "./_lib/formatLong/index.js";
import { formatRelative } from "./_lib/formatRelative/index.js";
import { localize } from "./_lib/localize/index.js";
import { match } from "./_lib/match/index.js";

/**
 * @category Locales
 * @summary Turkish locale.
 * @language Turkish
 * @iso-639-2 tur
 * @author Alpcan Aydın [@alpcanaydin](https://github.com/alpcanaydin)
 * @author Berkay Sargın [@berkaey](https://github.com/berkaey)
 * @author Fatih Bulut [@bulutfatih](https://github.com/bulutfatih)
 * @author Ismail Demirbilek [@dbtek](https://github.com/dbtek)
 * @author İsmail Kayar [@ikayar](https://github.com/ikayar)
 *
 *
 */
export const tr: Locale = {
  code: "tr",
  formatDistance: formatDistance,
  formatLong: formatLong,
  formatRelative: formatRelative,
  localize: localize,
  match: match,
  options: {
    weekStartsOn: 1 /* Monday */,
    firstWeekContainsDate: 1,
  },
};
