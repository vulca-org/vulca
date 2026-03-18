/**
 * 数据导出工具
 * 支持将表格数据导出为 CSV 和 JSON 格式
 */

import type { LeaderboardEntry } from '../types/types';

/**
 * 将数据转换为 CSV 格式
 */
export function convertToCSV<T extends object>(data: T[], columns?: { key: string; label: string }[]): string {
  if (data.length === 0) return '';
  
  // 如果没有指定列，则使用数据的所有键
  const headers = columns
    ? columns.map(col => col.label)
    : Object.keys((data[0] ?? {}) as Record<string, unknown>);
  
  const rows = data.map(row => {
    const values = columns
      ? columns.map(col => {
          const value = getNestedValue(row, col.key);
          return formatCSVValue(value);
        })
      : Object.values(row as Record<string, unknown>).map(value => formatCSVValue(value));
    return values.join(',');
  });
  
  return [headers.join(','), ...rows].join('\n');
}

/**
 * 格式化 CSV 值，处理特殊字符
 */
function formatCSVValue(value: unknown): string {
  if (value === null || value === undefined) return '';
  
  const stringValue = String(value);
  
  // 如果包含逗号、换行符或引号，需要用引号包裹并转义内部引号
  if (stringValue.includes(',') || stringValue.includes('\n') || stringValue.includes('"')) {
    return `"${stringValue.replace(/"/g, '""')}"`;
  }
  
  return stringValue;
}

/**
 * 获取嵌套对象的值
 * 例如: getNestedValue(obj, 'model.name') 获取 obj.model.name
 */
function getNestedValue(obj: unknown, path: string): unknown {
  return path.split('.').reduce<unknown>((current, key) => {
    if (typeof current === 'object' && current !== null && key in current) {
      return (current as Record<string, unknown>)[key];
    }
    return undefined;
  }, obj);
}

/**
 * 导出排行榜数据为 CSV
 */
export function exportLeaderboardToCSV(entries: LeaderboardEntry[]): string {
  const columns = [
    { key: 'rank', label: '排名' },
    { key: 'model.name', label: '模型名称' },
    { key: 'model.organization', label: '组织' },
    { key: 'score', label: '综合分' },
    { key: 'model.metrics.rhythm', label: '格律韵律' },
    { key: 'model.metrics.composition', label: '构图色彩' },
    { key: 'model.metrics.narrative', label: '叙事逻辑' },
    { key: 'model.metrics.emotion', label: '情感表达' },
    { key: 'model.metrics.creativity', label: '创意新颖' },
    { key: 'model.metrics.cultural', label: '文化契合' },
    { key: 'winRate', label: '胜率(%)' },
    { key: 'battles', label: '对战数' },
    { key: 'change', label: '排名变化' },
    { key: 'model.releaseDate', label: '发布日期' },
  ];
  
  return convertToCSV(entries, columns);
}

/**
 * 导出排行榜数据为 JSON
 */
export function exportLeaderboardToJSON(entries: LeaderboardEntry[]): string {
  // 精简数据，只导出关键信息
  const simplifiedData = entries.map(entry => ({
    rank: entry.rank,
    model: {
      id: entry.model.id,
      name: entry.model.name,
      organization: entry.model.organization,
      version: entry.model.version,
      category: entry.model.category,
      releaseDate: entry.model.releaseDate,
    },
    score: entry.score,
    metrics: entry.model.metrics,
    winRate: entry.winRate,
    battles: entry.battles,
    change: entry.change,
  }));
  
  return JSON.stringify(simplifiedData, null, 2);
}

/**
 * 下载文件
 */
export function downloadFile(content: string, filename: string, type: string = 'text/plain'): void {
  const blob = new Blob([content], { type: `${type};charset=utf-8;` });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  // 清理 URL 对象
  URL.revokeObjectURL(url);
}

/**
 * 导出数据的统一接口
 */
export function exportData(
  data: LeaderboardEntry[],
  format: 'csv' | 'json',
  filename?: string
): void {
  const timestamp = new Date().toISOString().split('T')[0];
  const defaultFilename = `export_${timestamp}`;
  
  if (format === 'csv') {
    const csv = exportLeaderboardToCSV(data as LeaderboardEntry[]);
    downloadFile(csv, filename || `${defaultFilename}.csv`, 'text/csv');
  } else if (format === 'json') {
    const json = exportLeaderboardToJSON(data as LeaderboardEntry[]);
    downloadFile(json, filename || `${defaultFilename}.json`, 'application/json');
  }
}

/**
 * 复制数据到剪贴板
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('Failed to copy to clipboard:', err);
    return false;
  }
}
