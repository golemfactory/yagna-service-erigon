import { format } from 'date-fns';
import { zonedTimeToUtc } from 'date-fns-tz';

export const renderDate = (date: string | undefined) =>
  date ? format(zonedTimeToUtc(date, new Date().getTimezoneOffset().toString()), 'dd.MM.yyyy HH:mm') : '------ ----';
