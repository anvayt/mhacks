// CSS custom properties ("--blue-end") in style objects; @types/react's CSSProperties doesn't list them.
import "react";

declare module "react" {
  interface CSSProperties {
    [key: `--${string}`]: string | number | undefined;
  }
}
