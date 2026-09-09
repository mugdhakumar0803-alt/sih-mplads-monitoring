import dayjs from "dayjs";

export function getSLAStatus(filedAt, slaDeadlineDays) {
  const deadline = dayjs(filedAt).add(slaDeadlineDays, "day");
  const now = dayjs();
  const diffHours = deadline.diff(now, "hour");

  if (diffHours < 0) {
    const overdueDays = Math.abs(Math.floor(diffHours / 24));
    return {
      isOverdue: true,
      label: `${overdueDays}d overdue`,
      color: "text-red-600",
    };
  }

  const days = Math.floor(diffHours / 24);
  const hours = diffHours % 24;
  return {
    isOverdue: false,
    label: `${days}d ${hours}h remaining`,
    color: diffHours < 24 ? "text-orange-600" : "text-green-600",
  };
}