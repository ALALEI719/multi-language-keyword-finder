"use client";

import { useState } from "react";
import {
  Languages,
  TrendingUp,
  ShoppingBag,
  PenLine,
  Building2,
  ChevronDown,
} from "lucide-react";

// ─── FAQ data ────────────────────────────────────────────────────────────────
const FAQ_ITEMS = [
  {
    q: "Are your Search Volume and Keyword Difficulty (KD) data accurate?",
    a: "Yes. Our metrics connect via API to authoritative global SEO databases. This ensures that the search volume and competition difficulty you see accurately reflect the current reality of your target market.",
  },
  {
    q: 'What is "Search Intent," and why is it crucial for multi-language SEO?',
    a: "Search intent is the primary goal a user has when typing a query. Our tool uses AI to identify the intent behind your original keyword and matches it with vocabulary in the target language that shares that exact same intent, boosting your conversion rates.",
  },
  {
    q: "Which languages and countries does this tool support?",
    a: "We support 50+ countries worldwide. Beyond mainstream languages, we excel at handling niche languages with complex cultural contexts, such as Japanese, Korean, Arabic, and Vietnamese.",
  },
  {
    q: "What is the difference between the Free version and the VIP version?",
    a: "Free visitors can experience our core AI intent-mining features for a limited number of countries. Upgrading to VIP allows unlimited simultaneous country queries and one-click CSV exports.",
  },
];

// ─── JSON-LD schema ───────────────────────────────────────────────────────────
const FAQ_JSON_LD = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: FAQ_ITEMS.map(({ q, a }) => ({
    "@type": "Question",
    name: q,
    acceptedAnswer: { "@type": "Answer", text: a },
  })),
};

// ─── Illustrations ────────────────────────────────────────────────────────────
function TranslationIllustration() {
  return (
    <div className="relative flex items-center justify-center w-full h-64 lg:h-80 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 overflow-hidden select-none">
      {/* background grid */}
      <svg
        className="absolute inset-0 w-full h-full opacity-10"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
            <path d="M 32 0 L 0 0 0 32" fill="none" stroke="#818cf8" strokeWidth="0.5" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
      </svg>

      {/* floating keyword cards */}
      <div className="relative z-10 flex flex-col items-center gap-4 w-full px-8">
        <div className="flex items-center gap-3 w-full max-w-xs">
          <span className="px-3 py-1.5 rounded-lg bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 text-sm font-mono whitespace-nowrap">
            Robot Lawn Mower
          </span>
          <div className="flex-1 border-t border-dashed border-slate-600" />
          <Languages className="text-indigo-400 w-5 h-5 flex-shrink-0" />
          <div className="flex-1 border-t border-dashed border-slate-600" />
          <span className="px-3 py-1.5 rounded-lg bg-violet-500/20 border border-violet-500/40 text-violet-300 text-sm font-mono whitespace-nowrap">
            mähroboter
          </span>
        </div>
        <div className="flex items-center gap-3 w-full max-w-xs opacity-75">
          <span className="px-3 py-1.5 rounded-lg bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 text-sm font-mono whitespace-nowrap">
            Cheap Flights
          </span>
          <div className="flex-1 border-t border-dashed border-slate-600" />
          <Languages className="text-indigo-400 w-5 h-5 flex-shrink-0" />
          <div className="flex-1 border-t border-dashed border-slate-600" />
          <span className="px-3 py-1.5 rounded-lg bg-violet-500/20 border border-violet-500/40 text-violet-300 text-sm font-mono whitespace-nowrap">
            Vols Low Cost
          </span>
        </div>
        <div className="flex items-center gap-3 w-full max-w-xs opacity-50">
          <span className="px-3 py-1.5 rounded-lg bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 text-sm font-mono whitespace-nowrap">
            Laptop
          </span>
          <div className="flex-1 border-t border-dashed border-slate-600" />
          <Languages className="text-indigo-400 w-5 h-5 flex-shrink-0" />
          <div className="flex-1 border-t border-dashed border-slate-600" />
          <span className="px-3 py-1.5 rounded-lg bg-violet-500/20 border border-violet-500/40 text-violet-300 text-sm font-mono whitespace-nowrap">
            Notebook
          </span>
        </div>
      </div>

      {/* decorative glow */}
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-48 h-24 bg-indigo-600/20 rounded-full blur-3xl pointer-events-none" />
    </div>
  );
}

function UseCaseIllustration() {
  const items = [
    { icon: ShoppingBag, label: "E-commerce", color: "text-emerald-400", bg: "bg-emerald-500/10 border-emerald-500/30" },
    { icon: PenLine, label: "Content Creator", color: "text-sky-400", bg: "bg-sky-500/10 border-sky-500/30" },
    { icon: Building2, label: "SEO Agency", color: "text-violet-400", bg: "bg-violet-500/10 border-violet-500/30" },
    { icon: TrendingUp, label: "Growth Marketer", color: "text-amber-400", bg: "bg-amber-500/10 border-amber-500/30" },
  ];
  return (
    <div className="relative flex items-center justify-center w-full h-64 lg:h-80 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 overflow-hidden select-none">
      <svg className="absolute inset-0 w-full h-full opacity-10" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse">
            <circle cx="2" cy="2" r="1" fill="#818cf8" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#dots)" />
      </svg>
      <div className="relative z-10 grid grid-cols-2 gap-4 p-6">
        {items.map(({ icon: Icon, label, color, bg }) => (
          <div key={label} className={`flex flex-col items-center gap-2 px-5 py-4 rounded-xl border ${bg}`}>
            <Icon className={`w-7 h-7 ${color}`} />
            <span className="text-xs font-semibold text-slate-300 whitespace-nowrap">{label}</span>
          </div>
        ))}
      </div>
      <div className="absolute top-0 right-0 w-40 h-40 bg-violet-600/10 rounded-full blur-3xl pointer-events-none" />
    </div>
  );
}

// ─── Accordion item ───────────────────────────────────────────────────────────
function AccordionItem({ q, a, open, onToggle }: { q: string; a: string; open: boolean; onToggle: () => void }) {
  return (
    <div className="border border-slate-700 rounded-xl overflow-hidden transition-colors hover:border-slate-600">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between gap-4 px-6 py-5 text-left bg-slate-800/60 hover:bg-slate-800 transition-colors"
        aria-expanded={open}
      >
        <span className="font-semibold text-slate-100 text-sm lg:text-base">{q}</span>
        <ChevronDown
          className={`w-5 h-5 text-indigo-400 flex-shrink-0 transition-transform duration-300 ${open ? "rotate-180" : ""}`}
        />
      </button>
      <div
        className={`grid transition-all duration-300 ease-in-out ${open ? "grid-rows-[1fr]" : "grid-rows-[0fr]"}`}
      >
        <div className="overflow-hidden">
          <p className="px-6 py-5 text-slate-400 text-sm lg:text-base leading-relaxed border-t border-slate-700/50">
            {a}
          </p>
        </div>
      </div>
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────
export default function SeoContentSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggle = (i: number) => setOpenIndex(openIndex === i ? null : i);

  return (
    <section className="bg-slate-950 text-slate-100">
      {/* ── Section 1: Why ── */}
      <div className="max-w-6xl mx-auto px-6 py-20 lg:py-28">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
          {/* Left: illustration */}
          <TranslationIllustration />

          {/* Right: text */}
          <div>
            <p className="text-indigo-400 font-semibold text-sm uppercase tracking-widest mb-3">
              The Core Problem
            </p>
            <h2 className="text-2xl lg:text-3xl font-bold text-white leading-snug mb-5">
              Why Direct Translation Isn't Enough for International SEO
            </h2>
            <p className="text-slate-400 leading-relaxed mb-6">
              When executing cross-border e-commerce or global content marketing, many marketers make a fatal mistake: plugging their native keywords into a translation tool and using the literal results. This rarely works because{" "}
              <strong className="text-slate-200">language translation ≠ true Search Intent.</strong>
            </p>
            <ul className="space-y-4 mb-7">
              {[
                {
                  title: "Cultural Differences & Slang",
                  body: 'While an English speaker searches for "Cheap Flights," a French user might search for "Vols Low Cost" rather than "Vols Bon Marché."',
                },
                {
                  title: "Platform Search Habits",
                  body: 'When buying a laptop, German users search for "Notebook" far more frequently than "Laptop."',
                },
                {
                  title: "Typos & Abbreviations",
                  body: "Many users omit diacritics or use specific abbreviations when searching.",
                },
              ].map(({ title, body }) => (
                <li key={title} className="flex gap-3">
                  <span className="mt-1 w-2 h-2 rounded-full bg-indigo-500 flex-shrink-0" />
                  <span className="text-slate-400 text-sm leading-relaxed">
                    <strong className="text-slate-200">{title}: </strong>
                    {body}
                  </span>
                </li>
              ))}
            </ul>
            <p className="text-slate-300 text-sm leading-relaxed rounded-xl border border-indigo-500/30 bg-indigo-500/5 px-5 py-4">
              Our tool utilizes AI to deeply analyze the real search habits and cultural nuances of your target country, helping you discover{" "}
              <strong className="text-indigo-300">high-potential, localized keywords.</strong>
            </p>
          </div>
        </div>
      </div>

      {/* divider */}
      <div className="max-w-6xl mx-auto px-6">
        <div className="border-t border-slate-800" />
      </div>

      {/* ── Section 2: Who ── */}
      <div className="max-w-6xl mx-auto px-6 py-20 lg:py-28">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
          {/* Left: text */}
          <div>
            <p className="text-violet-400 font-semibold text-sm uppercase tracking-widest mb-3">
              Use Cases
            </p>
            <h2 className="text-2xl lg:text-3xl font-bold text-white leading-snug mb-5">
              Who Needs a Multi-Language Keyword Explorer?
            </h2>
            <p className="text-slate-400 leading-relaxed mb-6">
              Whether you are a beginner running a Shopify store or an experienced SEO expert, this tool will save you{" "}
              <strong className="text-slate-200">hours of manual research time.</strong>
            </p>
            <ul className="space-y-5">
              {[
                {
                  icon: ShoppingBag,
                  title: "Cross-Border E-commerce Sellers",
                  body: 'Uncover "blue ocean" product keywords in niche markets, optimize your product listings, and lower your CPC.',
                  color: "text-emerald-400",
                  ring: "ring-emerald-500/30",
                  bg: "bg-emerald-500/10",
                },
                {
                  icon: PenLine,
                  title: "Global Content Creators & Bloggers",
                  body: "Understand the exact questions users are asking. Create articles that perfectly match local search intent.",
                  color: "text-sky-400",
                  ring: "ring-sky-500/30",
                  bg: "bg-sky-500/10",
                },
                {
                  icon: Building2,
                  title: "International SEO Agencies",
                  body: "Generate multi-language keyword reports with a single click. Export directly to CSV.",
                  color: "text-violet-400",
                  ring: "ring-violet-500/30",
                  bg: "bg-violet-500/10",
                },
              ].map(({ icon: Icon, title, body, color, ring, bg }) => (
                <li key={title} className="flex gap-4">
                  <span className={`mt-0.5 p-2 rounded-lg ring-1 ${ring} ${bg} flex-shrink-0`}>
                    <Icon className={`w-4 h-4 ${color}`} />
                  </span>
                  <span className="text-slate-400 text-sm leading-relaxed">
                    <strong className="text-slate-200 block mb-0.5">{title}</strong>
                    {body}
                  </span>
                </li>
              ))}
            </ul>
          </div>

          {/* Right: illustration */}
          <UseCaseIllustration />
        </div>
      </div>

      {/* divider */}
      <div className="max-w-6xl mx-auto px-6">
        <div className="border-t border-slate-800" />
      </div>

      {/* ── Section 3: FAQ ── */}
      <div className="max-w-3xl mx-auto px-6 py-20 lg:py-28">
        <div className="text-center mb-12">
          <p className="text-indigo-400 font-semibold text-sm uppercase tracking-widest mb-3">
            Got Questions?
          </p>
          <h2 className="text-2xl lg:text-3xl font-bold text-white">
            Frequently Asked Questions
          </h2>
        </div>

        <div className="flex flex-col gap-3">
          {FAQ_ITEMS.map((item, i) => (
            <AccordionItem
              key={i}
              q={item.q}
              a={item.a}
              open={openIndex === i}
              onToggle={() => toggle(i)}
            />
          ))}
        </div>
      </div>

      {/* ── JSON-LD FAQ Schema ── */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(FAQ_JSON_LD) }}
      />
    </section>
  );
}
