export const mockWorks = [
  {
    id: "W-2024-001",
    title: "Hand Pump Installation — Rampur Cluster",
    category: "Drinking Water",
    district: "Bareilly",
    agency: "BSNL Works Div.",
    sanctioned: 4200000,
    spent: 4850000,
    progress: 92,
    status: "Delayed",
    overdueDays: 47,
    geoTag: true,
    flags: ["Cost Overrun"],
  },
  {
    id: "W-2024-002",
    title: "Rural Road — Sector 14 to Tikonia",
    category: "Roads",
    district: "Lucknow",
    agency: "PWD UP",
    sanctioned: 8500000,
    spent: 8490000,
    progress: 100,
    status: "Completed",
    overdueDays: 0,
    geoTag: true,
    flags: [],
  },
  {
    id: "W-2024-003",
    title: "Community Hall — Jalesar Village",
    category: "Community Hall",
    district: "Etah",
    agency: "Gram Panchayat",
    sanctioned: 3000000,
    spent: 890000,
    progress: 24,
    status: "Stalled",
    overdueDays: 112,
    geoTag: false,
    flags: ["Delayed", "No Geo-Tag"],
  },
  {
    id: "W-2024-004",
    title: "Streetlight — NH-28 Corridor",
    category: "Streetlights",
    district: "Bareilly",
    agency: "UPPCL",
    sanctioned: 1800000,
    spent: 1800000,
    progress: 100,
    status: "Completed",
    overdueDays: 0,
    geoTag: true,
    flags: [],
  },
  {
    id: "W-2024-005",
    title: "School Building Renovation",
    category: "Education",
    district: "Etah",
    agency: "Basic Shiksha Vibhag",
    sanctioned: 5500000,
    spent: 3200000,
    progress: 58,
    status: "In Progress",
    overdueDays: 0,
    geoTag: true,
    flags: [],
  },
];

export const statusColors = {
  Completed: "bg-green-100 text-green-700",
  "In Progress": "bg-blue-100 text-blue-700",
  Delayed: "bg-orange-100 text-orange-700",
  Stalled: "bg-red-100 text-red-700",
};
export const mockFundEligibility = [
  {
    workId: "W-2024-001",
    title: "Hand Pump Installation — Rampur Cluster",
    eligible: false,
    verifiedCompletion: 42.5,
    requiredPercent: 75,
    blockingReasons: [
      "No verified photo for 'mid' stage",
      "1 unresolved citizen grievance open on this work",
    ],
  },
  {
    workId: "W-2024-002",
    title: "Rural Road — Sector 14 to Tikonia",
    eligible: true,
    verifiedCompletion: 100,
    requiredPercent: 75,
    blockingReasons: [],
  },
  {
    workId: "W-2024-003",
    title: "Community Hall — Jalesar Village",
    eligible: false,
    verifiedCompletion: 24,
    requiredPercent: 75,
    blockingReasons: [
      "No geo-tag on any uploaded photo",
      "Work stalled 112 days past deadline",
      "3 unresolved citizen grievances open on this work",
    ],
  },
];
export const mockGrievances = [
  {
    id: "GRV-4471",
    workId: "W-2024-003",
    workTitle: "Community Hall — Jalesar Village",
    description: "This work is marked in-progress but nothing has been built at this site for months.",
    filedBy: "Ramesh Kumar",
    filedAt: "2026-08-10T10:00:00Z",
    slaDeadlineDays: 7,
    escalationLevel: "district",
    status: "open",
  },
  {
    id: "GRV-4472",
    workId: "W-2024-001",
    workTitle: "Hand Pump Installation — Rampur Cluster",
    description: "Cost seems inflated compared to similar hand pumps in nearby villages.",
    filedBy: "Sunita Devi",
    filedAt: "2026-09-01T09:00:00Z",
    slaDeadlineDays: 7,
    escalationLevel: "district",
    status: "open",
  },
];

export const escalationLabels = {
  district: "District Authority",
  state: "State Nodal Authority",
  mp: "Member of Parliament",
  ministry: "Ministry",
};
export const mockCompliance = {
  mpId: "MP-0231",
  scAllocationPercent: 11.2,
  scRequiredPercent: 15,
  stAllocationPercent: 8.1,
  stRequiredPercent: 7.5,
  priorityAreaPercent: 17.4,
  priorityAreaRequiredPercent: 15,
};

export const mockEscalation = {
  workId: "W-2024-003",
  workTitle: "Community Hall — Jalesar Village",
  district: "Etah",
  overdueDays: 112,
  progress: 24,
  status: "Stalled",
  timeline: [
    { date: "Aug 10", event: "Grievance filed by citizen", by: "Ramesh Kumar" },
    { date: "Aug 17", event: "SLA deadline missed — auto-escalated to District", by: "System" },
    { date: "Aug 20", event: "District acknowledged, investigation ordered", by: "District Collector" },
    { date: "Aug 27", event: "No resolution in 7 days — escalated to State", by: "System" },
  ],
  forceMajeure: [
    { district: "Pilibhit", status: "exempted", reason: "Flood — NDMA Declaration Jul 12 - Aug 3, 2026", worksExempted: 4 },
    { district: "Etah", status: "none", reason: "No calamity declared" },
  ],
};
export const mockSystemicPatterns = [
  {
    district: "Etah",
    escalatedCases: 4,
    period: "This Quarter",
    severity: "high",
  },
  {
    district: "Bareilly",
    escalatedCases: 2,
    period: "This Quarter",
    severity: "medium",
  },
  {
    district: "Lucknow",
    escalatedCases: 0,
    period: "This Quarter",
    severity: "low",
  },
];
export function getDashboardStats() {
  const totalSanctioned = mockWorks.reduce((sum, w) => sum + w.sanctioned, 0);
  const totalSpent = mockWorks.reduce((sum, w) => sum + w.spent, 0);
  const completed = mockWorks.filter((w) => w.status === "Completed").length;
  const activeAnomalies = mockWorks.filter((w) => w.flags.length > 0).length;

  return {
    totalSanctioned,
    totalSpent,
    utilizationPercent: ((totalSpent / totalSanctioned) * 100).toFixed(1),
    completed,
    totalWorks: mockWorks.length,
    activeAnomalies,
    statusBreakdown: {
      Completed: mockWorks.filter((w) => w.status === "Completed").length,
      "In Progress": mockWorks.filter((w) => w.status === "In Progress").length,
      Delayed: mockWorks.filter((w) => w.status === "Delayed").length,
      Stalled: mockWorks.filter((w) => w.status === "Stalled").length,
    },
  };
}