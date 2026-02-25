/** 日期格式化 */
export function formatDate(date: string | Date, fmt = 'YYYY-MM-DD'): string {
  const d = typeof date === 'string' ? new Date(date) : date
  const map: Record<string, number> = {
    YYYY: d.getFullYear(),
    MM: d.getMonth() + 1,
    DD: d.getDate(),
    HH: d.getHours(),
    mm: d.getMinutes(),
    ss: d.getSeconds(),
  }
  return fmt.replace(/YYYY|MM|DD|HH|mm|ss/g, (match) =>
    String(map[match]).padStart(2, '0')
  )
}
