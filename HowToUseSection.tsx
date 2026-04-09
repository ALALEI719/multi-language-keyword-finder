"use client";

import {
  KeyRound,
  Globe2,
  SearchCode,
  Sparkles,
  MousePointerClick,
  BarChart3,
  Lightbulb,
} from "lucide-react";

// ─── Step data ────────────────────────────────────────────────────────────────
const STEPS = [
  {
    num: "01",
    label: "Keyword Discovery",
    color: "from-indigo-500 to-violet-500",
    ring: "ring-indigo-500/20",
    glow: "bg-indigo-500/10",
    borderAccent: "border-l-indigo-500",
    actions: [
      { icon: KeyRound,         text: "Enter your Ahrefs API Token in the field above" },
      { icon: Globe2,           text: "Choose your source language and target country" },
      { icon: SearchCode,       text: 'Enter a keyword and click "Discover Keywords"' },
      {
        icon: Sparkles,
        text: (
          <>
            The tool translates your keyword and uses Ahrefs to find{" "}
            <strong className="text-slate-200">
              real search terms used in the target market
            </strong>
          </>
        ),
        highlight: true,
      },
    ],
  },
  {
    num: "02",
    label: "Deep Analysis",
    color: "from-violet-500 to-fuchsia-500",
    ring: "ring-violet-500/20",
    glow: "bg-violet-500/10",
    borderAccent: "border-l-violet-500",
    actions: [
      { icon: BarChart3,          text: "Pick the highest-volume keyword that matches your intent" },
      {
        icon: MousePointerClick,
        text: (
          <>
            Click{" "}
            <strong className="text-slate-200">"Deep Analysis"</strong> for
            full data + all related terms
          </>
        ),
        highlight: true,
      },
    ],
  },
];

// ─── Action row ───────────────────────────────────────────────────────────────
function ActionRow({
  icon: Icon,
  text,
  index,
  highlight,
}: {
  icon: React.ElementType;
  text: React.ReactNode;
  index: number;
  highlight?: boolean;
}) {
  return (
    <div
      className={`flex items-start gap-3 rounded-xl px-4 py-3 transition-colors ${
        highlight ? "bg-white/5 ring-1 ring-white/10" : "hover:bg-white/[0.03]"
      }`}
    >
      <div className="mt-0.5 flex-shrink-0 flex items-center justify-center w-7 h-7 rounded-lg bg-slate-700/80 ring-1 ring-white/10">
        <Icon className="w-3.5 h-3.5 text-slate-300" />
      </div>
      <div className="flex items-center gap-2 min-w-0">
        <span className="text-xs font-bold text-slate-600 flex-shrink-0 tabular-nums">
          {String(index + 1).padStart(2, "0")}
        </span>
        <p className="text-sm text-slate-400 leading-relaxed">{text}</p>
      </div>
    </div>
  );
}

// ─── Step card ────────────────────────────────────────────────────────────────
function StepCard({
  num,
  label,
  color,
  ring,
  glow,
  borderAccent,
  actions,
}: (typeof STEPS)[0]) {
  return (
    <div
      className={`relative flex flex-col gap-1 rounded-2xl border border-slate-800 bg-slate-900 overflow-hidden ring-1 ${ring}`}
    >
      {/* top accent bar */}
      <div className={`h-1 w-full bg-gradient-to-r ${color}`} />

      <div className="px-7 pt-6 pb-7 flex flex-col gap-5">
        {/* header */}
        <div className="flex items-center gap-4">
          <span
            className={`text-5xl font-black leading-none bg-gradient-to-br ${color} bg-clip-text text-transparent select-none`}
          >
            {num}
          </span>
          <div>
            <p className="text-[0.7rem] font-semibold uppercase tracking-widest text-slate-500 mb-0.5">
              Step
            </p>
            <h3 className="text-lg font-bold text-slate-100">{label}</h3>
          </div>
        </div>

        {/* vertical timeline connector + actions */}
        <div className={`relative border-l-2 ${borderAccent} ml-3.5 pl-5 flex flex-col gap-2`}>
          {actions.map((a, i) => (
            <ActionRow key={i} icon={a.icon} text={a.text} index={i} highlight={a.highlight} />
          ))}
        </div>
      </div>

      {/* subtle glow */}
      <div
        className={`pointer-events-none absolute -bottom-8 -right-8 w-40 h-40 ${glow} rounded-full blur-3xl`}
      />
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────
export default function HowToUseSection() {
  return (
    <section className="bg-slate-950 py-20 lg:py-28">
      <div className="max-w-5xl mx-auto px-6">
        {/* section header */}
        <div className="text-center mb-14">
          <p className="text-indigo-400 font-semibold text-sm uppercase tracking-widest mb-3">
            Get Started
          </p>
          <h2 className="text-2xl lg:text-3xl font-bold text-white">
            💡 How to Use
          </h2>
          <p className="mt-3 text-slate-400 text-sm max-w-md mx-auto">
            Two focused steps to go from a source-language keyword to
            high-traffic, intent-matched local terms.
          </p>
        </div>

        {/* step cards */}
        <div className="grid lg:grid-cols-2 gap-6 mb-10">
          {STEPS.map((step) => (
            <StepCard key={step.num} {...step} />
          ))}
        </div>

        {/* Why Two Steps callout */}
        <div className="relative rounded-2xl border border-amber-500/25 bg-gradient-to-br from-amber-500/8 via-amber-500/5 to-transparent overflow-hidden px-7 py-6 ring-1 ring-amber-500/15">
          {/* left accent */}
          <div className="absolute left-0 top-0 h-full w-1 bg-gradient-to-b from-amber-400 to-amber-600 rounded-l-2xl" />

          <div className="flex gap-4 items-start">
            <div className="flex-shrink-0 mt-0.5 flex items-center justify-center w-10 h-10 rounded-xl bg-amber-500/15 ring-1 ring-amber-500/30">
              <Lightbulb className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <p className="text-sm font-bold text-amber-300 mb-2 tracking-wide">
                🎯 Pro Tip — Why Two Steps?
              </p>
              <p className="text-sm text-slate-400 leading-relaxed max-w-2xl">
                Direct translations are often{" "}
                <strong className="text-slate-200">not</strong> what
                target-market users actually search for. For example,{" "}
                <span className="font-mono text-xs bg-slate-800 rounded px-1.5 py-0.5 text-slate-300">
                  Robot Lawn Mower
                </span>{" "}
                translates to German{" "}
                <span className="font-mono text-xs bg-slate-800 rounded px-1.5 py-0.5 text-red-400 line-through">
                  Roboter-Rasenmäher
                </span>{" "}
                (only 70 searches/mo), but German users actually search for{" "}
                <span className="font-mono text-xs bg-indigo-900/60 border border-indigo-500/40 rounded px-1.5 py-0.5 text-indigo-300 font-bold">
                  mähroboter
                </span>{" "}
                (tens of thousands/mo). Ahrefs suggestions surface the{" "}
                <strong className="text-slate-200">
                  real high-traffic keywords.
                </strong>
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
