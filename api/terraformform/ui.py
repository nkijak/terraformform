from dataclasses import dataclass

from htmy import html, Context, Component


@dataclass
class IndexPage:
    def htmy(self, context: Context) -> Component:
        return (
            html.DOCTYPE.html,
            html.html(
                html.head(
                    # Some metadata
                    html.title("TerraformForm"),
                    html.meta.charset(),
                    html.meta.viewport(),
                    # daisy
                    html.link(
                        href="https://cdn.jsdelivr.net/npm/daisyui@4.12.23/dist/full.min.css",
                        rel="stylesheet",
                        type="text/css",
                    ),
                    # TailwindCSS
                    html.script(src="https://cdn.tailwindcss.com"),
                    # HTMX
                    html.script(src="https://unpkg.com/htmx.org@2.0.2"),
                ),
                html.body(
                    # Page content: lazy-loaded user list.
                    # html.div(hx_get="", hx_trigger="load", hx_swap="outerHTML"),
                    class_=(
                        "h-screen w-screen flex flex-col items-center justify-center "
                        "gap-4 base-100"
                    ),
                ),
                data_theme="corporate",
            ),
        )
