import React from "react";
import { Link } from "react-router-dom";
import panchsetuLogo from "../assets/panchsetu-logo.png";

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-white text-gray-800">

      {/* ================= HEADER ================= */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50 backdrop-blur-md bg-white/90">
        <div className="max-w-7xl mx-auto px-5 md:px-8 py-3.5 flex items-center justify-between">

          {/* Logo + Branding */}
          <div className="flex items-center gap-4">
            <img
              src={panchsetuLogo}
              alt="PANCHSETU Logo"
              className="w-14 h-14 md:w-16 md:h-16 object-contain"
            />
            <div>
              <h1 className="text-xl md:text-2xl font-extrabold tracking-wide text-navy">
                PANCHSETU
              </h1>
              <p className="text-xs text-gray-600 font-medium">
                MPLADS Monitoring & Accountability Platform
              </p>
              <p className="text-[11px] text-gray-400">
                Ministry of Statistics & Programme Implementation
              </p>
            </div>
          </div>

          {/* Login + Register */}
          <div className="hidden md:flex items-center gap-4">
            <Link
              to="/register"
              className="text-navy font-semibold text-sm hover:text-accent transition"
            >
              Register
            </Link>
            <Link
              to="/login"
              className="flex items-center gap-2 bg-navy text-white px-5 py-2.5 rounded-lg text-sm font-semibold hover:bg-navy/90 transition shadow-sm"
            >
              Login
              <span>→</span>
            </Link>
          </div>
        </div>

        {/* ================= NAVIGATION ================= */}
        <div className="bg-navy shadow-inner">
          <div className="max-w-7xl mx-auto px-5 md:px-8">
            <div className="flex items-center gap-8 py-2.5 text-sm font-medium overflow-x-auto">
              <a href="#home" className="text-white/90 hover:text-white transition whitespace-nowrap">Home</a>
              <a href="#about" className="text-white/90 hover:text-white transition whitespace-nowrap">About</a>
              <a href="#features" className="text-white/90 hover:text-white transition whitespace-nowrap">Features</a>
              <a href="#workflow" className="text-white/90 hover:text-white transition whitespace-nowrap">How It Works</a>
              <a href="#stakeholders" className="text-white/90 hover:text-white transition whitespace-nowrap">Stakeholders</a>
              <Link
                to="/login"
                className="ml-auto bg-accent text-white px-4 py-1.5 rounded-md text-xs font-semibold hover:opacity-90 transition whitespace-nowrap"
              >
                Enter Portal
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* ================= HERO ================= */}
      <section
        id="home"
        className="relative overflow-hidden bg-gradient-to-br from-[#f5f8fc] via-white to-[#eef4fa]"
      >
        <div className="absolute -right-32 -top-32 w-96 h-96 rounded-full bg-navy/5 blur-xl"></div>
        <div className="absolute -left-32 bottom-0 w-80 h-80 rounded-full bg-accent/5 blur-xl"></div>

        <div className="relative max-w-7xl mx-auto px-5 md:px-8 py-16 md:py-20">
          <div className="grid lg:grid-cols-2 gap-12 items-center">

            {/* LEFT CONTENT */}
            <div>
              <div className="inline-flex items-center gap-2 bg-[#e8eef6] text-navy px-4 py-1.5 rounded-full text-xs font-semibold mb-6">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                Intelligent Governance Platform
              </div>

              <h2 className="text-4xl md:text-5xl lg:text-6xl font-extrabold leading-tight text-navy tracking-tight">
                Smarter Monitoring.
                <br />
                <span className="text-[#28598c]">Stronger Accountability.</span>
              </h2>

              <p className="mt-6 text-base md:text-lg text-gray-600 leading-relaxed max-w-xl">
                PANCHSETU brings AI-powered analytics, project monitoring,
                citizen participation, and risk-based alerts together to
                strengthen transparency in MPLADS implementation.
              </p>

              <div className="mt-8 flex flex-wrap gap-4">
                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 bg-navy text-white px-6 py-3 rounded-lg font-semibold hover:bg-navy/90 transition shadow-md hover:shadow-lg"
                >
                  Access PANCHSETU
                  <span>→</span>
                </Link>
                <a
                  href="#about"
                  className="inline-flex items-center gap-2 border border-navy/30 text-navy px-6 py-3 rounded-lg font-semibold hover:bg-navy hover:text-white transition"
                >
                  Explore Platform
                </a>
              </div>

              <div className="mt-8 flex flex-wrap gap-6 text-xs md:text-sm font-medium text-gray-500">
                <span className="flex items-center gap-1.5"><strong className="text-green-600">✓</strong> AI Analytics</span>
                <span className="flex items-center gap-1.5"><strong className="text-green-600">✓</strong> Risk Alerts</span>
                <span className="flex items-center gap-1.5"><strong className="text-green-600">✓</strong> Citizen Transparency</span>
              </div>
            </div>

            {/* RIGHT VISUAL - CLEAN EMBEDDED UI */}
            <div>
              <div className="bg-white border border-gray-200 rounded-2xl shadow-xl overflow-hidden">
                <div className="bg-navy px-6 py-4 text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-[11px] text-blue-200 font-semibold uppercase tracking-wider">
                        Monitoring Overview
                      </p>
                      <h3 className="text-lg font-bold mt-0.5">MPLADS Insights</h3>
                    </div>
                    <div className="w-10 h-10 bg-white/10 rounded-lg flex items-center justify-center">
                      <img src={panchsetuLogo} alt="" className="w-7 h-7 object-contain" />
                    </div>
                  </div>
                </div>

                <div className="p-6">
                  <div className="grid grid-cols-2 gap-3.5">
                    <StatCard number="01" title="Anomaly Detection" description="Identify unusual patterns" />
                    <StatCard number="02" title="Project Tracking" description="Monitor execution progress" />
                    <StatCard number="03" title="Citizen Feedback" description="Ground-level verification" />
                    <StatCard number="04" title="Risk Alerts" description="Prioritize critical cases" />
                  </div>

                  {/* Embedded Flow Banner (Replaced Overlapping Floating Badge) */}
                  <div className="mt-4 border border-gray-200 rounded-xl p-4 bg-gray-50/50">
                    <div className="flex justify-between items-center mb-3">
                      <div>
                        <p className="text-[11px] text-gray-500 font-semibold uppercase">Accountability Flow</p>
                        <p className="font-bold text-navy text-sm">Monitor → Verify → Act</p>
                      </div>
                      <span className="inline-flex items-center gap-1 text-green-700 bg-green-50 px-2.5 py-1 rounded-full text-xs font-semibold border border-green-200">
                        <span className="w-1.5 h-1.5 bg-green-600 rounded-full"></span>
                        Active
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <div className="h-2 flex-1 bg-navy rounded-full"></div>
                      <div className="h-2 flex-1 bg-[#28598c] rounded-full"></div>
                      <div className="h-2 flex-1 bg-accent rounded-full"></div>
                    </div>

                    <div className="mt-3 pt-3 border-t border-gray-200/60 flex items-center justify-between text-xs text-gray-600">
                      <span className="font-medium text-gray-500">Governance Model</span>
                      <span className="font-bold text-navy">Data → Insight → Action</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* ================= ABOUT ================= */}
      <section id="about" className="py-20 bg-white">
        <div className="max-w-6xl mx-auto px-5 md:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <p className="text-xs font-bold tracking-widest uppercase text-accent">
              About PANCHSETU
            </p>
            <h2 className="text-3xl md:text-4xl font-bold text-navy mt-2">
              Bridging Data, Governance & Citizens
            </h2>
            <div className="w-12 h-1 bg-accent mx-auto mt-4 rounded-full"></div>
            <p className="mt-6 text-gray-600 text-base md:text-lg leading-relaxed">
              PANCHSETU acts as an intelligent monitoring layer for
              MPLADS implementation, transforming project and financial
              data into actionable insights, risk alerts, and accountability
              signals.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-12">
            <Pillar number="01" title="Detect" />
            <Pillar number="02" title="Verify" />
            <Pillar number="03" title="Predict" />
            <Pillar number="04" title="Escalate" />
            <Pillar number="05" title="Prevent" />
          </div>
        </div>
      </section>

      {/* ================= FEATURES ================= */}
      <section id="features" className="py-20 bg-[#f7f9fc]">
        <div className="max-w-7xl mx-auto px-5 md:px-8">
          <div className="mb-12 text-center md:text-left">
            <p className="text-xs font-bold tracking-widest uppercase text-accent">
              Platform Capabilities
            </p>
            <h2 className="text-3xl md:text-4xl font-bold text-navy mt-2">
              One Platform. Multiple Layers of Accountability.
            </h2>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard icon="◈" title="AI Anomaly Detection" text="Identify unusual expenditure patterns, cost deviations and potential financial irregularities." />
            <FeatureCard icon="◎" title="Duplicate Work Detection" text="Detect potentially duplicated projects using semantic and geographical similarity." />
            <FeatureCard icon="◷" title="Delay Analysis" text="Track project timelines and identify works requiring early intervention." />
            <FeatureCard icon="⌖" title="Geo-Tagged Verification" text="Support evidence-based monitoring through location-aware project verification." />
            <FeatureCard icon="✓" title="Compliance Monitoring" text="Validate project categories and monitor important statutory requirements." />
            <FeatureCard icon="!" title="Risk-Based Alerts" text="Prioritize high-risk cases and route them to the appropriate authority." />
          </div>
        </div>
      </section>

      {/* ================= WORKFLOW ================= */}
      <section id="workflow" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-5 md:px-8">
          <div className="text-center mb-12">
            <p className="text-xs font-bold tracking-widest uppercase text-accent">
              Accountability Loop
            </p>
            <h2 className="text-3xl md:text-4xl font-bold text-navy mt-2">
              From Detection to Action
            </h2>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
            <WorkflowStep number="01" title="Project Data" />
            <WorkflowStep number="02" title="AI Analysis" />
            <WorkflowStep number="03" title="Risk Detection" />
            <WorkflowStep number="04" title="Verification" />
            <WorkflowStep number="05" title="Escalation" />
            <WorkflowStep number="06" title="Action" />
          </div>

          <div className="mt-10 text-center">
            <p className="text-gray-600 max-w-2xl mx-auto text-sm md:text-base">
              PANCHSETU doesn't just identify a problem. It tracks what
              happens after the problem is identified.
            </p>
          </div>
        </div>
      </section>

      {/* ================= STAKEHOLDERS ================= */}
      <section id="stakeholders" className="py-20 bg-[#f7f9fc]">
        <div className="max-w-7xl mx-auto px-5 md:px-8">
          <div className="text-center mb-12">
            <p className="text-xs font-bold tracking-widest uppercase text-accent">
              Unified Governance
            </p>
            <h2 className="text-3xl md:text-4xl font-bold text-navy mt-2">
              Designed for Every Stakeholder
            </h2>
          </div>

          <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-5">
            <Stakeholder title="Member of Parliament" text="Constituency-level project monitoring, risks and fund utilization." />
            <Stakeholder title="District Authority" text="Detailed execution monitoring, grievances and corrective action." />
            <Stakeholder title="State Authority" text="State-level trends, escalations and performance monitoring." />
            <Stakeholder title="Ministry" text="National-level analytics and systemic risk identification." />
          </div>
        </div>
      </section>

      {/* ================= CTA ================= */}
      <section className="relative overflow-hidden bg-navy text-white">
        <div className="absolute right-0 top-0 w-96 h-96 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/3"></div>

        <div className="relative max-w-4xl mx-auto px-5 py-16 text-center">
          <h2 className="text-3xl md:text-4xl font-bold">
            Building a More Transparent MPLADS Ecosystem
          </h2>
          <p className="mt-4 text-blue-100 text-base md:text-lg">
            Data-driven insights. Early warnings. Stronger accountability.
          </p>
          <Link
            to="/login"
            className="inline-flex items-center gap-3 mt-8 bg-accent text-white px-8 py-3.5 rounded-lg font-bold hover:opacity-90 transition shadow-lg"
          >
            Enter PANCHSETU Portal
            <span>→</span>
          </Link>
        </div>
      </section>

      {/* ================= FOOTER ================= */}
      <footer className="bg-[#0d2239] text-gray-300">
        <div className="max-w-7xl mx-auto px-5 md:px-8 py-10">
          <div className="flex flex-col md:flex-row justify-between gap-8">
            <div className="flex gap-4 items-start">
              <img src={panchsetuLogo} alt="PANCHSETU" className="w-12 h-12 object-contain" />
              <div>
                <h3 className="text-white font-bold text-lg">PANCHSETU</h3>
                <p className="text-xs text-gray-400 mt-1 max-w-md">
                  AI-Powered MPLADS Monitoring & Accountability Platform
                </p>
              </div>
            </div>

            <div className="text-xs md:text-right">
              <p className="text-gray-300 font-medium">
                Ministry of Statistics & Programme Implementation
              </p>
              <p className="mt-1 text-gray-400">
                Technology solution for intelligent monitoring and analytics.
              </p>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-8 pt-5 text-xs text-gray-500 text-center">
            © 2026 PANCHSETU • Prototype Platform
          </div>
        </div>
      </footer>
    </div>
  );
};

/* ========================================================= */
/* HELPER COMPONENTS */
/* ========================================================= */

const StatCard = ({ number, title, description }) => (
  <div className="border border-gray-200 bg-white rounded-xl p-3.5 hover:border-navy/40 transition hover:shadow-sm">
    <div className="text-[11px] font-bold text-accent">{number}</div>
    <h4 className="font-bold text-navy mt-1 text-xs md:text-sm">{title}</h4>
    <p className="text-[11px] text-gray-500 mt-0.5 leading-tight">{description}</p>
  </div>
);

const Pillar = ({ number, title }) => (
  <div className="border border-gray-200 bg-white p-4 text-center rounded-xl hover:shadow-md hover:border-navy/20 transition">
    <div className="text-xs font-bold text-accent">{number}</div>
    <h3 className="font-bold text-navy mt-1.5 text-sm">{title}</h3>
  </div>
);

const FeatureCard = ({ icon, title, text }) => (
  <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg hover:-translate-y-1 transition duration-200">
    <div className="w-10 h-10 rounded-lg bg-[#e8eef6] text-navy flex items-center justify-center text-lg font-bold">
      {icon}
    </div>
    <h3 className="text-base font-bold text-navy mt-4">{title}</h3>
    <p className="text-xs md:text-sm text-gray-600 mt-2 leading-relaxed">{text}</p>
  </div>
);

const WorkflowStep = ({ number, title }) => (
  <div className="bg-white border border-gray-200 rounded-xl p-4 text-center hover:shadow-md transition">
    <div className="text-[11px] font-bold text-accent">STEP {number}</div>
    <h3 className="font-bold text-navy mt-1.5 text-xs md:text-sm">{title}</h3>
  </div>
);

const Stakeholder = ({ title, text }) => (
  <div className="bg-white border border-gray-200 rounded-xl p-6 text-center hover:shadow-md transition">
    <div className="w-10 h-10 mx-auto rounded-full bg-[#e8eef6] flex items-center justify-center text-navy font-bold text-sm">
      ✓
    </div>
    <h3 className="font-bold text-navy mt-4 text-sm md:text-base">{title}</h3>
    <p className="text-xs md:text-sm text-gray-600 mt-2 leading-relaxed">{text}</p>
  </div>
);

export default LandingPage;