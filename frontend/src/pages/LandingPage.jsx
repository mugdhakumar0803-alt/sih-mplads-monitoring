import React from "react";
import { Link } from "react-router-dom";
import panchsetuLogo from "../assets/panchsetu-logo.png";

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-white text-gray-800">

      {/* ================= TOP BAR ================= */}
      <div className="bg-[#f5f7fa] border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-5 md:px-8 py-2 flex justify-between items-center text-xs text-gray-600">
          <p>Government of India • Reference Context</p>

          <div className="hidden sm:flex items-center gap-5">
            <span>भारत सरकार</span>
            <span>Accessibility</span>
            <span>A-</span>
            <span>A</span>
            <span>A+</span>
          </div>
        </div>
      </div>

      {/* ================= HEADER ================= */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">

        <div className="max-w-7xl mx-auto px-5 md:px-8 py-4 flex items-center justify-between">

          {/* LOGO + BRAND */}
          <div className="flex items-center gap-4">

            <img
              src={panchsetuLogo}
              alt="PANCHSETU Logo"
              className="w-16 h-16 md:w-20 md:h-20 object-contain"
            />

            <div>
              <h1 className="text-2xl md:text-3xl font-bold tracking-wide text-[#17365D]">
                PANCHSETU
              </h1>

              <p className="text-xs md:text-sm text-gray-600 mt-1">
                MPLADS Monitoring & Accountability Platform
              </p>

              <p className="text-[11px] md:text-xs text-gray-500 mt-1">
                AI-Powered Monitoring & Governance Solution
              </p>
            </div>
          </div>

          {/* LOGIN + REGISTER */}
          <div className="hidden md:flex items-center gap-5">

            <Link
              to="/register"
              className="text-[#17365D] font-semibold text-sm hover:underline"
            >
              Register
            </Link>

            <Link
              to="/login"
              className="flex items-center gap-2 bg-[#17365D] text-white px-6 py-3 rounded-md font-semibold hover:bg-[#28598c] transition shadow-sm"
            >
              Login
              <span>→</span>
            </Link>

          </div>
        </div>

        {/* ================= NAVIGATION ================= */}
        <div className="bg-[#17365D]">

          <div className="max-w-7xl mx-auto px-5 md:px-8">

            <div className="flex items-center gap-8 py-3 text-sm font-medium overflow-x-auto">

              <a
                href="#home"
                className="text-white hover:text-[#F4B400] transition whitespace-nowrap"
              >
                Home
              </a>

              <a
                href="#about"
                className="text-white hover:text-[#F4B400] transition whitespace-nowrap"
              >
                About
              </a>

              <a
                href="#features"
                className="text-white hover:text-[#F4B400] transition whitespace-nowrap"
              >
                Features
              </a>

              <a
                href="#workflow"
                className="text-white hover:text-[#F4B400] transition whitespace-nowrap"
              >
                How It Works
              </a>

              <a
                href="#stakeholders"
                className="text-white hover:text-[#F4B400] transition whitespace-nowrap"
              >
                Stakeholders
              </a>

              <Link
                to="/login"
                className="ml-auto bg-[#F4B400] text-white px-5 py-2 rounded-md font-semibold hover:bg-[#d99e00] transition whitespace-nowrap"
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

        {/* Background Shapes */}
        <div className="absolute -right-32 -top-32 w-96 h-96 rounded-full bg-[#17365D]/5"></div>

        <div className="absolute -left-32 bottom-0 w-80 h-80 rounded-full bg-[#F4B400]/5"></div>

        <div className="relative max-w-7xl mx-auto px-5 md:px-8 py-20 md:py-24">

          <div className="grid lg:grid-cols-2 gap-14 items-center">

            {/* ================= LEFT CONTENT ================= */}
            <div>

              <div className="inline-flex items-center gap-2 bg-[#e8eef6] text-[#17365D] px-4 py-2 rounded-full text-sm font-semibold mb-6">

                <span className="w-2 h-2 bg-green-600 rounded-full"></span>

                Intelligent Governance Platform

              </div>

              <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-[1.1] text-[#17365D]">

                Smarter Monitoring.
                <br />

                <span className="text-[#28598c]">
                  Stronger Accountability.
                </span>

              </h2>

              <p className="mt-7 text-lg md:text-xl text-gray-600 leading-relaxed max-w-2xl">

                PANCHSETU brings AI-powered analytics, project monitoring,
                citizen participation and risk-based alerts together to
                strengthen transparency and accountability in MPLADS
                implementation.

              </p>

              {/* BUTTONS */}
              <div className="mt-9 flex flex-wrap gap-4">

                <Link
                  to="/login"
                  className="inline-flex items-center gap-3 bg-[#17365D] text-white px-7 py-3.5 rounded-md font-semibold hover:bg-[#28598c] transition shadow-lg"
                >
                  Access PANCHSETU
                  <span>→</span>
                </Link>

                <a
                  href="#about"
                  className="inline-flex items-center gap-2 border border-[#17365D] text-[#17365D] px-7 py-3.5 rounded-md font-semibold hover:bg-[#17365D] hover:text-white transition"
                >
                  Explore Platform
                </a>

              </div>

              {/* HIGHLIGHTS */}
              <div className="mt-8 flex flex-wrap gap-6 text-sm text-gray-500">

                <span>✓ AI-Powered Analytics</span>

                <span>✓ Risk-Based Monitoring</span>

                <span>✓ Citizen Transparency</span>

              </div>

            </div>

            {/* ================= RIGHT VISUAL ================= */}
            <div className="relative">

              <div className="bg-white border border-gray-200 rounded-2xl shadow-xl overflow-hidden">

                {/* CARD HEADER */}
                <div className="bg-[#17365D] px-6 py-5 text-white">

                  <div className="flex items-center justify-between">

                    <div>

                      <p className="text-xs text-blue-200 uppercase tracking-wider">
                        Monitoring Overview
                      </p>

                      <h3 className="text-xl font-bold mt-1">
                        MPLADS Insights
                      </h3>

                    </div>

                    <div className="w-12 h-12 bg-white/10 rounded-xl flex items-center justify-center">

                      <img
                        src={panchsetuLogo}
                        alt="PANCHSETU"
                        className="w-9 h-9 object-contain"
                      />

                    </div>

                  </div>

                </div>

                {/* CARD CONTENT */}
                <div className="p-6">

                  <div className="grid grid-cols-2 gap-4">

                    <StatCard
                      number="01"
                      title="Anomaly Detection"
                      description="Identify unusual patterns"
                    />

                    <StatCard
                      number="02"
                      title="Project Tracking"
                      description="Monitor execution progress"
                    />

                    <StatCard
                      number="03"
                      title="Citizen Feedback"
                      description="Ground-level verification"
                    />

                    <StatCard
                      number="04"
                      title="Risk Alerts"
                      description="Prioritize critical cases"
                    />

                  </div>

                  {/* ACCOUNTABILITY FLOW */}
                  <div className="mt-5 border border-gray-200 rounded-xl p-5">

                    <div className="flex justify-between items-center mb-4">

                      <div>

                        <p className="text-xs text-gray-500">
                          Accountability Flow
                        </p>

                        <p className="font-semibold text-[#17365D]">
                          Monitor → Verify → Act
                        </p>

                      </div>

                      <span className="text-green-600 font-semibold text-sm">
                        Active
                      </span>

                    </div>

                    <div className="flex items-center gap-2">

                      <div className="h-2 flex-1 bg-[#17365D] rounded-full"></div>

                      <div className="h-2 flex-1 bg-[#28598c] rounded-full"></div>

                      <div className="h-2 flex-1 bg-[#F4B400] rounded-full"></div>

                    </div>

                  </div>

                </div>
              </div>

              {/* FLOATING CARD */}
              <div className="absolute -bottom-5 -left-5 bg-white border border-gray-200 shadow-lg rounded-xl px-5 py-4">

                <p className="text-xs text-gray-500">
                  Governance
                </p>

                <p className="font-bold text-[#17365D]">
                  Data → Insight → Action
                </p>

              </div>

            </div>
          </div>
        </div>
      </section>

      {/* ================= ABOUT ================= */}
      <section
        id="about"
        className="py-20 bg-white"
      >

        <div className="max-w-6xl mx-auto px-5 md:px-8">

          <div className="text-center max-w-3xl mx-auto">

            <p className="text-sm font-bold tracking-widest uppercase text-[#F4B400]">
              About PANCHSETU
            </p>

            <h2 className="text-3xl md:text-4xl font-bold text-[#17365D] mt-3">
              Bridging Data, Governance & Citizens
            </h2>

            <div className="w-16 h-1 bg-[#F4B400] mx-auto mt-5"></div>

            <p className="mt-7 text-gray-600 text-lg leading-relaxed">

              PANCHSETU acts as an intelligent monitoring layer for
              MPLADS implementation, transforming project and financial
              data into actionable insights, risk alerts and accountability
              signals.

            </p>

          </div>

          {/* FIVE PILLARS */}
          <div className="grid md:grid-cols-5 gap-4 mt-14">

            <Pillar number="01" title="Detect" />

            <Pillar number="02" title="Verify" />

            <Pillar number="03" title="Predict" />

            <Pillar number="04" title="Escalate" />

            <Pillar number="05" title="Prevent" />

          </div>

        </div>
      </section>

      {/* ================= FEATURES ================= */}
      <section
        id="features"
        className="py-20 bg-[#f7f9fc]"
      >

        <div className="max-w-7xl mx-auto px-5 md:px-8">

          <div className="mb-12">

            <p className="text-sm font-bold tracking-widest uppercase text-[#F4B400]">
              Platform Capabilities
            </p>

            <h2 className="text-3xl md:text-4xl font-bold text-[#17365D] mt-3">
              One Platform. Multiple Layers of Accountability.
            </h2>

          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">

            <FeatureCard
              icon="◈"
              title="AI Anomaly Detection"
              text="Identify unusual expenditure patterns, cost deviations and potential financial irregularities."
            />

            <FeatureCard
              icon="◎"
              title="Duplicate Work Detection"
              text="Detect potentially duplicated projects using semantic and geographical similarity."
            />

            <FeatureCard
              icon="◷"
              title="Delay Analysis"
              text="Track project timelines and identify works requiring early intervention."
            />

            <FeatureCard
              icon="⌖"
              title="Geo-Tagged Verification"
              text="Support evidence-based monitoring through location-aware project verification."
            />

            <FeatureCard
              icon="✓"
              title="Compliance Monitoring"
              text="Validate project categories and monitor important statutory requirements."
            />

            <FeatureCard
              icon="!"
              title="Risk-Based Alerts"
              text="Prioritize high-risk cases and route them to the appropriate authority."
            />

          </div>
        </div>
      </section>

      {/* ================= WORKFLOW ================= */}
      <section
        id="workflow"
        className="py-20 bg-white"
      >

        <div className="max-w-7xl mx-auto px-5 md:px-8">

          <div className="text-center mb-14">

            <p className="text-sm font-bold tracking-widest uppercase text-[#F4B400]">
              Accountability Loop
            </p>

            <h2 className="text-3xl md:text-4xl font-bold text-[#17365D] mt-3">
              From Detection to Action
            </h2>

          </div>

          <div className="grid md:grid-cols-6 gap-3">

            <WorkflowStep
              number="01"
              title="Project Data"
            />

            <WorkflowStep
              number="02"
              title="AI Analysis"
            />

            <WorkflowStep
              number="03"
              title="Risk Detection"
            />

            <WorkflowStep
              number="04"
              title="Verification"
            />

            <WorkflowStep
              number="05"
              title="Escalation"
            />

            <WorkflowStep
              number="06"
              title="Action"
            />

          </div>

          <div className="mt-10 text-center">

            <p className="text-gray-600 max-w-3xl mx-auto">

              PANCHSETU doesn't just identify a problem. It tracks what
              happens after the problem is identified.

            </p>

          </div>

        </div>
      </section>

      {/* ================= STAKEHOLDERS ================= */}
      <section
        id="stakeholders"
        className="py-20 bg-[#f7f9fc]"
      >

        <div className="max-w-7xl mx-auto px-5 md:px-8">

          <div className="text-center mb-12">

            <p className="text-sm font-bold tracking-widest uppercase text-[#F4B400]">
              Unified Governance
            </p>

            <h2 className="text-3xl md:text-4xl font-bold text-[#17365D] mt-3">
              Designed for Every Stakeholder
            </h2>

          </div>

          <div className="grid md:grid-cols-4 gap-5">

            <Stakeholder
              title="Member of Parliament"
              text="Constituency-level project monitoring, risks and fund utilization."
            />

            <Stakeholder
              title="District Authority"
              text="Detailed execution monitoring, grievances and corrective action."
            />

            <Stakeholder
              title="State Authority"
              text="State-level trends, escalations and performance monitoring."
            />

            <Stakeholder
              title="Ministry"
              text="National-level analytics and systemic risk identification."
            />

          </div>

        </div>
      </section>

      {/* ================= CTA ================= */}
      <section className="relative overflow-hidden bg-[#17365D] text-white">

        <div className="absolute right-0 top-0 w-96 h-96 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/3"></div>

        <div className="relative max-w-5xl mx-auto px-5 py-20 text-center">

          <h2 className="text-3xl md:text-4xl font-bold">
            Building a More Transparent MPLADS Ecosystem
          </h2>

          <p className="mt-5 text-blue-100 text-lg">
            Data-driven insights. Early warnings. Stronger accountability.
          </p>

          <Link
            to="/login"
            className="inline-flex items-center gap-3 mt-8 bg-[#F4B400] text-white px-8 py-3.5 rounded-md font-bold hover:bg-[#d99e00] transition shadow-lg"
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

            {/* FOOTER BRAND */}
            <div className="flex gap-4 items-start">

              <img
                src={panchsetuLogo}
                alt="PANCHSETU"
                className="w-14 h-14 object-contain"
              />

              <div>

                <h3 className="text-white font-bold text-xl">
                  PANCHSETU
                </h3>

                <p className="text-sm mt-2 max-w-md">
                  AI-Powered MPLADS Monitoring & Accountability Platform
                </p>

              </div>

            </div>

            {/* FOOTER INFO */}
            <div className="text-sm md:text-right">

              <p className="text-gray-400">
                Proposed Digital Solution for MPLADS Monitoring
              </p>

              <p className="mt-2 text-gray-500">
                Technology solution for intelligent monitoring and analytics.
              </p>

            </div>

          </div>

          <div className="border-t border-gray-700 mt-8 pt-5 text-xs text-gray-500 text-center">

            © 2026 PANCHSETU • Prototype Platform

          </div>

        </div>

      </footer>

    </div>
  );
};


/* ========================================================= */
/* STAT CARD */
/* ========================================================= */

const StatCard = ({ number, title, description }) => (

  <div className="border border-gray-200 rounded-xl p-4 hover:border-[#17365D]/30 transition">

    <div className="text-xs font-bold text-[#F4B400]">
      {number}
    </div>

    <h4 className="font-bold text-[#17365D] mt-2 text-sm">
      {title}
    </h4>

    <p className="text-xs text-gray-500 mt-1">
      {description}
    </p>

  </div>

);


/* ========================================================= */
/* PILLAR */
/* ========================================================= */

const Pillar = ({ number, title }) => (

  <div className="border border-gray-200 bg-white p-5 text-center rounded-lg hover:shadow-md transition">

    <div className="text-xs font-bold text-[#F4B400]">
      {number}
    </div>

    <h3 className="font-bold text-[#17365D] mt-2">
      {title}
    </h3>

  </div>

);


/* ========================================================= */
/* FEATURE CARD */
/* ========================================================= */

const FeatureCard = ({ icon, title, text }) => (

  <div className="bg-white border border-gray-200 rounded-xl p-7 hover:shadow-lg hover:-translate-y-1 transition duration-300">

    <div className="w-11 h-11 rounded-lg bg-[#e8eef6] text-[#17365D] flex items-center justify-center text-xl font-bold">
      {icon}
    </div>

    <h3 className="text-lg font-bold text-[#17365D] mt-5">
      {title}
    </h3>

    <p className="text-sm text-gray-600 mt-3 leading-relaxed">
      {text}
    </p>

  </div>

);


/* ========================================================= */
/* WORKFLOW STEP */
/* ========================================================= */

const WorkflowStep = ({ number, title }) => (

  <div className="relative">

    <div className="bg-white border border-gray-200 rounded-xl p-5 text-center hover:shadow-md transition">

      <div className="text-xs font-bold text-[#F4B400]">
        STEP {number}
      </div>

      <h3 className="font-bold text-[#17365D] mt-2">
        {title}
      </h3>

    </div>

  </div>

);


/* ========================================================= */
/* STAKEHOLDER */
/* ========================================================= */

const Stakeholder = ({ title, text }) => (

  <div className="bg-white border border-gray-200 rounded-xl p-7 text-center hover:shadow-lg transition">

    <div className="w-12 h-12 mx-auto rounded-full bg-[#e8eef6] flex items-center justify-center text-[#17365D] font-bold">
      ✓
    </div>

    <h3 className="font-bold text-[#17365D] mt-5">
      {title}
    </h3>

    <p className="text-sm text-gray-600 mt-3 leading-relaxed">
      {text}
    </p>

  </div>

);


export default LandingPage;