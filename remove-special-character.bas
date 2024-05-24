' this script will take an open active spreadsheet (native app) remove duplicate, and then all special characters from the selected range, then order from A to Z
''' made by LP Roux '''
Sub RemoveDuplicatesEmptyAndSpecial()
    Dim ws As Worksheet
    Dim rng As Range
    Dim cell As Range
    Dim i As Long
    Dim cellValue As String
    Dim hasSpecial As Boolean
  
    Set ws = ActiveSheet ' Work on the active sheet
    ' Dynamically set the range to include all used cells in Column A
    Set rng = ws.Range("A2:A" & ws.Cells(ws.Rows.Count, "A").End(xlUp).Row)
  
    ' Remove duplicates
    rng.RemoveDuplicates Columns:=1, Header:=xlNo
  
    ' Iterate from the bottom to the top (to safely delete or clear cells)
    For i = rng.Rows.Count To 1 Step -1
        Set cell = rng.Cells(i, 1)
        cellValue = cell.Value
        hasSpecial = False
          
        ' Check if the cell is empty or starts with an apostrophe
        If Len(Trim(cellValue)) = 0 Or Left(cellValue, 1) = "'" Then
            hasSpecial = True
        Else
            ' Check each character in the cell
            For j = 1 To Len(cellValue)
                ' Allowing alphanumeric, space, minus sign, and apostrophe
                If Not (Mid(cellValue, j, 1) Like "[A-Za-z0-9 ',-]") Then
                    hasSpecial = True
                    Exit For
                End If
            Next j
        End If
          
        ' If the cell is empty, starts with an apostrophe, or contains a special character outside the allowed list, clear the cell
        If hasSpecial Then
            cell.ClearContents
        End If
    Next i

    ' Sort column A in ascending order, excluding the header
    ws.Range("A2:A" & ws.Cells(ws.Rows.Count, "A").End(xlUp).Row).Sort Key1:=ws.Range("A2"), Order1:=xlAscending, Header:=xlNo
End Sub