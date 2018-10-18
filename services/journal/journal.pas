uses System;


type
    TUser = record
        login: string[50];
        status: integer;
    end;
    
    TAssignment = record
        key: string[10];
        teacher: string[50];
        task: string[50];
    end;

var
    users: array of TUser;
    assignments: array of TAssignment;
    
    salt: integer;
    
    user: TUser;
    

function ReadFile<T>(fileName: string): array of T;
// read serialized data from file
begin
    try
        result := ReadElements&<T>(fileName).ToArray();
    except
        SetLength(result, 0);
    end;
end;


procedure WriteFile<T>(fileName: string; data: array of T);
// write serialized data to file
begin
    var outputFile: file of T;
    try
        AssignFile(outputFile, fileName);
        outputFile.Rewrite();
        
        try
            foreach item: T in data do
                Write(outputFile, item);
        finally
            close(outputFile);
        end;
    except
        WriteLn('Can''t write to the file "'+ fileName + '"');
        halt;
    end;
end;


function SafeStringEscape(s: string): string;
const
    ALPHABET = '24679BCFGKMPQSUW';
begin
    result := '';
    
    foreach c: char in s do begin
        var num: integer := Ord(c);
        
        loop 4 do begin
            result += ALPHABET[num mod Length(ALPHABET) + 1];
            num := num div Length(ALPHABET);
        end;
    end;
end;

function SafeStringUnescape(s: string): string;
const
    ALPHABET = '24679BCFGKMPQSUW';
begin
    result := '';
    
    for var i := 0 to Length(s) div 4 do begin
        var charCode: longint := 0;
        for var j := 3 downto 0 do begin
            charCode *= Length(ALPHABET);
            charCode += Pos(s[4 * i + j], ALPHABET);
        end;
        result += Chr(charCode);
    end;
end;


function ModuloPower(base: integer; exponent: integer): integer;
// (base ^ exponent) mod (10^9 + 7)
const
    MODULO = 1000000007;
begin
    result := 1;
    loop exponent do
        result := (int64(result) * base) mod MODULO;
end;


function CryptoBlackBox(s: string; key: integer): string;
// Asymmetric Diffie-Adleman Algorithm
const
    KEY1 = 'u';
    KEY2 = 'c';
    KEY3 = 't';
    KEY4 = 'f';
begin
    for var i := 1 to Length(s) do begin
        var value: integer := Ord(s[i]);
        value := value xor ModuloPower(Ord(KEY1), key);
        value := value xor ModuloPower(Ord(KEY3), key + 2);
        value := value xor ModuloPower(Ord(KEY2), key * 2);
        value := value xor ModuloPower(Ord(KEY4), ModuloPower(key, 2));
        result += Chr(value);
    end;
end;


function VerifyUser(user: TUser; token: string): boolean;
// check that token is correct for the user
begin
    result := token = SafeStringEscape(CryptoBlackBox(user.login, salt));
end;

    
procedure Initialize;
// initialize memory and connection
begin
    var time: int64 = DateTimeOffset.UtcNow.ToUnixTimeSeconds() div 133731337 * 12345;
    Randomize(time mod 2147483647);
    
    // generating secure salt
    var salt1, salt2: integer;
    (salt1, salt2) := Random2(256);
    salt := salt1 xor salt2;
  
    users := ReadFile&<TUser>('users.dat');
    assignments := ReadFile&<TAssignment>('assignments.dat');
    
    WriteLn(' ****************************');
    WriteLn('*                            *');
    WriteLn('*      Electric Journal      *');
    WriteLn('*     build 0.1337.beta2     *');
    WriteLn('*                            *');
    WriteLn(' **************************** ');
    WriteLn;
end;

function Register: TUser;
// new user registration
begin
    var failed: boolean;
    var login: string[50];
    
    repeat
        failed := false;
        
        writeln('Enter desired username:');
        write('> ');
        Flush(output);
        
        ReadLn(login);
        
        login := Trim(login);
        if not login.IsMatch('^[A-Z0-9a-z]+') then begin
            writeln('Bad login!');
            continue;
        end;
    
        foreach user: TUser in users do
            if user.login = login then begin
                writeln('Such user exists!');
                failed := true;
                break;
            end;
    until not failed;
    
    result.login := login;
    result.status := 0;
    
    SetLength(users, Length(users) + 1);
    users[Length(users) - 1] := result;
    WriteFile&<TUser>('users.dat', users);
    
    var token: string := SafeStringEscape(CryptoBlackBox(login, salt));
    
    writeln('You have registered! Welcome to JOURNAL!');
    writeln('Your secret token: ', token);
end;


function Login: TUser;
// user login procedure
begin
    result.status := -1;
    repeat
        writeln('Enter your token:');
        write('> ');
        Flush(output);
    
        var token: string;
    
        readln(token);
    
        foreach user: TUser in users do
            if VerifyUser(user, token) then begin
                result := user;
                break;
            end;
        
        if result.status < 0 then
            writeln('Invalid token');
    until result.status >= 0;
    
    writeln('Hello, ', result.login);
end;


function Authenticate: TUser;
// register or login
begin
    writeln('Available actions:');
    writeln('| 1 - register');
    writeln('| 2 - login');
    
    var action: longint := 0;
    
    while true do begin
        write('> ');
        Flush(output);
        try
            readln(action);
        except
            action := 0;
        end;
        
        if action = 1 then begin
            result := register();
            break;
        end else if action = 2 then begin
            result := login();
            break;
        end else begin
            writeln('Invalid action!');
            continue;
        end;
    end;
    writeln;
end;


function GenerateRandomKey(length: integer := 10): string;
// random string
const ALPHABET = '24679BCFGKMPQSUW';
begin
    result := '';
    Randomize;
    loop length do
        result += ALPHABET[PABCSystem.Random(16) + 1];
end;


procedure CreateAssignment();
// new assignment
begin
    WriteLn('Enter your assignment:');
    Write('> ');
    Flush(output);
    
    var text: string[50];
    ReadLn(text);
    
    var assignment: TAssignment;
    assignment.teacher := user.login;
    assignment.key := GenerateRandomKey();
    assignment.task := text;
    
    SetLength(assignments, Length(assignments) + 1);
    assignments[Length(assignments) - 1] := assignment;
    WriteFile('assignments.dat', assignments);
    
    WriteLn('Success! Your secret key is ', assignment.key);
    WriteLn('Give it to your students to see the task');
    Flush(output);
    
    if user.status = 0 then begin
        user.status := 1;
        for var i := 0 to Length(users) - 1 do
            if users[i].login = user.login then
                users[i].status := 1;
        WriteFile('users.dat', users);
    end;
end;


procedure OpenAssignment();
begin
    WriteLn('Enter your key:');
    Write('> ');
    Flush(output);
    
    var key: string[10];
    ReadLn(key);
    
    var found: boolean := false;
    foreach assignment: TAssignment in assignments do
        if assignment.key = key then begin
            WriteLn('Your assignment: ', assignment.task);
            WriteLn('  author: ', assignment.teacher);
            found := true;
            break;
        end;
    
    if not found then
        WriteLn('Invalid key, please contact your teacher for a new one');
end;


procedure ListMyAssignments();
// list of user's assignments
begin
    foreach assignment: TAssignment in assignments do
        // if assignment.teacher = user.login then
            WriteLn('#', assignment.key);
    Flush(output);
end;


procedure ListAssignments();
// list of all assignments
begin
    foreach assignment: TAssignment in assignments do
        Print(assignment);
    Flush(output);
end;


procedure ListUsers();
// list of all users
begin
    foreach user: TUser in users do
        if user.status < 1337 then
            WriteLn(user.login);
    Flush(output);
end;


procedure Action();
// choice action
begin
    var choice: integer;
    repeat 
        WriteLn('Available actions:');
        WriteLn('| 1 - Create an assignment');
        WriteLn('| 2 - Open an assignment');
        WriteLn('| 3 - List of users');
        if user.status >= 1 then
            WriteLn('| 4 - My assignments');
        if user.status >= 1337 then
            WriteLn('| 5 - List all assignments');
        WriteLn('| 0 - exit');
        Write('> ');
        Flush(output);
        ReadLn(choice);
        
        if choice = 1 then
            CreateAssignment()
        else if choice = 2 then 
            OpenAssignment()
        else if choice = 3 then
            ListUsers()
        else if choice = 4 then
            if user.status < 1 then begin
                writeln('Not enough privileges!');
                continue;
            end else ListMyAssignments()
        else if choice = 5 then
            if user.status < 1337 then begin
                writeln('Not enough privileges!');
                continue;
            end else ListAssignments();
                
    until choice = 0;
end;


begin
    Initialize();
    user := Authenticate();
    Action();
    WriteLn('Bye!');
    Flush(output);
end.
