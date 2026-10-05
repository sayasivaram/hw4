/**
 * An original, simplified bulldog face -- not a reproduction of any
 * official Yale mark -- used purely as a collegiate-style decorative motif
 * (nav brand, footer, hero watermark). Single-path, `currentColor`-based so
 * it can be recolored/sized from CSS wherever it's used.
 */
export default function BulldogMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 100 92" className={className} fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* ears */}
      <path
        d="M18 14c-8 2-13 11-10 21 2 7 7 11 13 12l5-20z"
        fill="currentColor"
      />
      <path
        d="M82 14c8 2 13 11 10 21-2 7-7 11-13 12l-5-20z"
        fill="currentColor"
      />
      {/* head */}
      <path
        d="M50 10c-18 0-32 13-32 30 0 10 5 18 12 23-3 3-5 7-5 11 0 9 11 14 25 14s25-5 25-14c0-4-2-8-5-11 7-5 12-13 12-23 0-17-14-30-32-30z"
        fill="currentColor"
      />
      {/* jowls */}
      <path d="M26 58c-6 3-10 9-10 15 0 7 7 12 15 12 5 0 9-2 12-6-9-3-15-11-17-21z" fill="currentColor" />
      <path d="M74 58c6 3 10 9 10 15 0 7-7 12-15 12-5 0-9-2-12-6 9-3 15-11 17-21z" fill="currentColor" />
      {/* eyes */}
      <circle cx="39" cy="42" r="5" fill="var(--bulldog-eye, #fff)" />
      <circle cx="61" cy="42" r="5" fill="var(--bulldog-eye, #fff)" />
      <circle cx="39" cy="42" r="2.2" fill="var(--bulldog-pupil, currentColor)" />
      <circle cx="61" cy="42" r="2.2" fill="var(--bulldog-pupil, currentColor)" />
      {/* snout + nose */}
      <ellipse cx="50" cy="56" rx="11" ry="8" fill="var(--bulldog-eye, #fff)" />
      <ellipse cx="50" cy="52" rx="5" ry="4" fill="var(--bulldog-pupil, currentColor)" />
      <path
        d="M41 60c3 4 6 6 9 6s6-2 9-6"
        stroke="var(--bulldog-pupil, currentColor)"
        strokeWidth="2.5"
        strokeLinecap="round"
        fill="none"
      />
    </svg>
  );
}
