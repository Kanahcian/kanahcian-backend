-- Issue #29: Account 表其實只是「大學生」名單。
--  1. rename 成 Student，讓命名對得上用途
--  2. 移除沒人讀寫的明文 Password 欄位
-- 純結構調整，不動既有資料列。
-- 在 Supabase SQL editor 執行：

ALTER TABLE public."Account" RENAME TO "Student";
ALTER TABLE public."Student" RENAME COLUMN "AccountID" TO "StudentID";
ALTER SEQUENCE public."Account_AccountID_seq" RENAME TO "Student_StudentID_seq";

ALTER TABLE public."Students_at_record" RENAME COLUMN "Account" TO "Student";
ALTER TABLE public."Students_at_record" RENAME CONSTRAINT "Account" TO "Student";

ALTER TABLE public."Student" DROP COLUMN IF EXISTS "Password";
