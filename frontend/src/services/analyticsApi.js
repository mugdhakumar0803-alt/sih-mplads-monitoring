import axios from "axios";

const BASE = "/api/analytics"; // proxy to your backend, or full URL if separate host

export const getFundUtilization = () => axios.get(`${BASE}/fund-utilization`).then(r => r.data);
export const getProgressVsUtilization = () => axios.get(`${BASE}/progress-vs-utilization`).then(r => r.data);
export const getRiskDistribution = () => axios.get(`${BASE}/risk-distribution`).then(r => r.data);
export const getConstituencyRanking = (metric = "completion") =>
  axios.get(`${BASE}/constituency-ranking`, { params: { metric } }).then(r => r.data);
export const getCitizenVerification = () => axios.get(`${BASE}/citizen-verification`).then(r => r.data);
export const getGrievanceTrend = () => axios.get(`${BASE}/grievance-trend`).then(r => r.data);
export const getComplianceScore = () => axios.get(`${BASE}/compliance-score`).then(r => r.data);
export const getRiskDrivers = (workId) => axios.get(`${BASE}/risk-drivers/${workId}`).then(r => r.data);