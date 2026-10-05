/**
 * An original shield/crest motif (not Yale's official seal) -- a generic
 * collegiate shield with a monogram and two stars, used as decorative
 * branding. `currentColor` for the shield outline so it can be recolored
 * from CSS.
 */
export default function CrestMark({ className, letter = "C" }: { className?: string; letter?: string }) {
  return (
    <svg viewBox="0 0 80 96" className={className} xmlns="http://www.w3.org/2000/svg">
      <path
        d="M4 4h72v40c0 28-18 44-36 48C22 88 4 72 4 44V4z"
        fill="none"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path d="M4 4h72v8H4z" fill="currentColor" />
      <text
        x="40"
        y="54"
        textAnchor="middle"
        fontFamily="Georgia, serif"
        fontWeight="700"
        fontSize="34"
        fill="currentColor"
      >
        {letter}
      </text>
      <path d="M22 70l3 7 7 1-5 5 1 7-6-4-6 4 1-7-5-5 7-1z" fill="currentColor" opacity="0.85" />
      <path d="M58 70l3 7 7 1-5 5 1 7-6-4-6 4 1-7-5-5 7-1z" fill="currentColor" opacity="0.85" />
    </svg>
  );
}
