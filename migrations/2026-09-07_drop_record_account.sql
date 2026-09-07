-- Issue #28: 移除未使用的 Record.Account 欄位
-- 169 筆 Record 的 Account 全為 NULL；參與學生已由 Students_at_record 表達。
-- DROP COLUMN 會自動移除其 FK constraint（backup 裡名為 "By"）。
-- 在 Supabase SQL editor 執行：

ALTER TABLE public."Record" DROP COLUMN IF EXISTS "Account";
