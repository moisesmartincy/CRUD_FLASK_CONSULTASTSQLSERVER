-- ====================================================================
-- BASE DE DATOS: concursoBaile
-- SCRIPT COMPLETO DE VISTAS, FUNCIONES, PROCEDIMIENTOS Y TRIGGERS
-- Motor: Microsoft SQL Server (T-SQL)
-- ====================================================================

USE concursoBaile;
GO

-- ====================================================================
-- 1. VISTA 1: Vista completa de los bailes
-- ====================================================================
CREATE OR ALTER VIEW vista1
AS
SELECT 
    (SELECT nombre + ' ' + paterno + ' ' + materno FROM Participante WHERE codPar = b.codParVar) AS Varon,
    (SELECT nombre + ' ' + paterno + ' ' + materno FROM Participante WHERE codPar = b.codParMuj) AS Mujer,
    (SELECT titulo FROM Musica WHERE codMus = b.codMus) AS Titulo_Musica,
    (SELECT nombre FROM Danza WHERE codDan = b.codDan) AS Tipo_Danza,
    (SELECT nombre + ' ' + paterno + ' ' + materno FROM Participante WHERE codPar = b.codCou) AS Coach,
    b.fecha AS Fecha_Baile
FROM Baile b;
GO

-- ====================================================================
-- 2. FUNCIÓN 1: dbo.obInst (Obtener Institución del Participante)
-- ====================================================================
CREATE OR ALTER FUNCTION dbo.obInst(@n VARCHAR(15), @p VARCHAR(15), @m VARCHAR(15)) 
RETURNS VARCHAR(100) 
AS 
BEGIN 
    DECLARE @nomIns VARCHAR(100);
    
    SELECT @nomIns = i.nombre 
    FROM Participante p
    INNER JOIN Institucion i ON p.codIns = i.codIns 
    WHERE p.nombre = @n 
      AND p.paterno = @p 
      AND p.materno = @m;
      
    RETURN ISNULL(@nomIns, 'Sin institución registrada o no encontrado');
END;
GO

-- ====================================================================
-- 3. FUNCIÓN 2: dbo.cantidad (Contar Participantes por Tipo)
-- Tipos: 'b' = Bailarín, 'j' = Jurado, 'c' = Coach
-- ====================================================================
CREATE OR ALTER FUNCTION dbo.cantidad(@t VARCHAR(2))
RETURNS INT
AS
BEGIN
    DECLARE @total INT;
    
    SELECT @total = COUNT(*)
    FROM Participante
    WHERE tipo = @t;
    
    RETURN ISNULL(@total, 0);
END;
GO

-- ====================================================================
-- 4. PROCEDIMIENTO ALMACENADO: mostrarBaile (Filtrar por Fecha)
-- ====================================================================
CREATE OR ALTER PROCEDURE mostrarBaile(@f DATE)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT * FROM vista1 WHERE Fecha_Baile = @f;
END;
GO

-- ====================================================================
-- 5. PROCEDIMIENTO CON CURSORES ANIDADOS: comprueba
-- Compara el puntaje total del baile contra la suma de puntajes del jurado
-- ====================================================================
CREATE OR ALTER PROCEDURE comprueba
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Cursor 1: Recorre la tabla Baile
    DECLARE c1 CURSOR LOCAL FOR
        SELECT nroBai, ptjeTotal FROM Baile;
    
    -- Cursor 2: Suma los puntajes de los jurados por baile
    DECLARE c2 CURSOR LOCAL FOR
        SELECT nroBai, SUM(ptje) FROM DetalleBaile GROUP BY nroBai;
    
    DECLARE @nb INT, @pb INT;
    DECLARE @nd INT, @pd INT;
    DECLARE @coincidencia BIT;
    
    OPEN c1;
    FETCH NEXT FROM c1 INTO @nb, @pb;
    
    WHILE @@FETCH_STATUS = 0
    BEGIN
        SET @coincidencia = 0;
        
        OPEN c2;
        FETCH NEXT FROM c2 INTO @nd, @pd;
        
        WHILE @@FETCH_STATUS = 0
        BEGIN
            IF @nb = @nd
            BEGIN
                SET @coincidencia = 1;
                IF @pb = @pd
                    PRINT 'Baile ' + CAST(@nb AS VARCHAR) + ': Puntaje = ' + CAST(@pb AS VARCHAR) + ' | Jurados = ' + CAST(@pd AS VARCHAR) + ' [IGUAL]';
                ELSE
                    PRINT 'Baile ' + CAST(@nb AS VARCHAR) + ': Puntaje = ' + CAST(@pb AS VARCHAR) + ' | Jurados = ' + CAST(@pd AS VARCHAR) + ' [DIFERENTE]';
                BREAK;
            END
            FETCH NEXT FROM c2 INTO @nd, @pd;
        END
        CLOSE c2;
        
        IF @coincidencia = 0
            PRINT 'Baile ' + CAST(@nb AS VARCHAR) + ': Sin detalles de jurados registrados.';
            
        FETCH NEXT FROM c1 INTO @nb, @pb;
    END
    
    CLOSE c1;
    DEALLOCATE c1;
    DEALLOCATE c2;
END;
GO

-- ====================================================================
-- 6. TABLAS Y TRIGGER DE AUDITORÍA (AFTER INSERT)
-- ====================================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Clientes')
BEGIN
    CREATE TABLE Clientes (
        ClienteID INT IDENTITY(1,1) PRIMARY KEY,
        Nombre VARCHAR(100) NOT NULL,
        Email VARCHAR(100),
        FechaRegistro DATETIME DEFAULT GETDATE()
    );
END;
GO

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'AuditoriaClientes')
BEGIN
    CREATE TABLE AuditoriaClientes (
        AuditoriaID INT IDENTITY(1,1) PRIMARY KEY,
        ClienteID INT NOT NULL,
        FechaCambio DATETIME NOT NULL,
        Accion VARCHAR(20) NOT NULL
    );
END;
GO

CREATE OR ALTER TRIGGER tgr_RegistrarNuevoCliente
ON Clientes
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO AuditoriaClientes (ClienteID, FechaCambio, Accion)
    SELECT ClienteID, GETDATE(), 'INSERT'
    FROM inserted;
END;
GO

