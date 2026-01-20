"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

export function Navigation() {
  const pathname = usePathname();

  return (
    <nav
      className="sticky top-0 z-50 w-full border-b border-white/10 glass-effect backdrop-blur-xl"
      aria-label="Main navigation"
    >
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link
          href="/"
          className="flex items-center gap-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background rounded-sm"
          aria-label="Commitment Broker Home"
        >
          {/* Logo SVG - abstract commitment loop icon */}
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="text-primary opacity-60"
            aria-hidden="true"
          >
            <circle
              cx="12"
              cy="12"
              r="8"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              className="opacity-40"
            />
            <path
              d="M8 12h8M12 8v8"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              className="opacity-60"
            />
          </svg>
          <span className="font-semibold tracking-tight text-foreground">
            Commitment Broker
          </span>
        </Link>
        <nav className="flex items-center gap-4 sm:gap-8" aria-label="Main navigation">
          <Link
            href="/"
            className={cn(
              "text-sm font-medium transition-colors hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background rounded-sm px-2 py-1",
              pathname === "/"
                ? "text-foreground"
                : "text-muted-foreground"
            )}
            aria-current={pathname === "/" ? "page" : undefined}
          >
            Commitments
          </Link>
          <Link
            href="/evaluation"
            className={cn(
              "text-sm font-medium transition-colors hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background rounded-sm px-2 py-1",
              pathname === "/evaluation"
                ? "text-foreground"
                : "text-muted-foreground"
            )}
            aria-current={pathname === "/evaluation" ? "page" : undefined}
          >
            Evaluation
          </Link>
        </nav>
      </div>
    </nav>
  );
}
