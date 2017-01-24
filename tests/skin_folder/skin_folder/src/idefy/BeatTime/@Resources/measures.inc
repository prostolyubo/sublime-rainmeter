; ----------------------------------
; MEASURES return .beat measures
; ----------------------------------

[measureBMTHour]
; This measure returns the BMT time
Measure=Time
TimeZone=+1
DayLightSavingTime=0
Format=%H

[measureBMTMin]
; This measure returns the BMT time
Measure=Time
TimeZone=+1
DayLightSavingTime=0
Format=%M

[measureBMTSec]
; This measure returns the BMT time
Measure=Time
TimeZone=+1
DayLightSavingTime=0
Format=%S

[measureBeatTime]
; Returns the date as YYYY-MM-DD
Measure=Calc
Formula=(([measureBMTHour:]*3600)+([measureBMTMin:]*60)+([measureBMTSec:])) / 86.4
DynamicVariables=1