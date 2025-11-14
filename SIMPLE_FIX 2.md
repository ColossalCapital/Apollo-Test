# Simple Fix for Enhanced Outputs

Due to syntax errors with complex f-strings, here's the simple approach:

## Keep the current simple versions but enhance them slightly

Instead of creating three massive new methods with complex string formatting, just:

1. **ISSUES_REPORT.md** - Keep simple, add:
   - Count of files with TODO/FIXME
   - List of cold files to review
   
2. **FUTURE_STATE.md** - Keep simple, add:
   - Show file:line for each planned feature
   - Group by type (TODO/FIXME/FUTURE)

3. **RESTRUCTURING_PLAN.md** - Keep simple, add:
   - Show days since edit for cold files
   - Specific ticket templates

## The issue

The complex f-strings with triple quotes and escaped characters cause syntax errors.

## Solution

Revert to the working version and make small, incremental improvements instead of massive rewrites.

Let me restore the working version now...
