# 📊 Análise Detalhada dos 8 Endpoints SOAP Selecionados
**Data:** 2025-07-31 14:27:39  
**Autor:** Paulo - Professional Services  
**Objetivo:** Análise técnica completa dos endpoints selecionados

## 🎯 Endpoints Selecionados para Análise

1. **`GetDocentes`**
2. **`GetCursos`**
3. **`GetAnosLect`**
4. **`GetPeriodos`**
5. **`GetCursos`**
6. **`GetPEstudos`**
7. **`GetTurmas`**
8. **`GetDisc`**
9. **`GetDiscHorario`**
10. **`EditLinhaHorario`**
11. **`PutHorario`**

---

## 📋 Resumo Executivo
- **Total de endpoints analisados:** 11
- **Endpoints encontrados:** 11/11 (100.0%)
- **Endpoints com erro:** 0

## 🔍 Análise Detalhada por Endpoint

### GetDocentes
**Status:** ✅ Disponível  
**Código:** 201  
**Descrição:** Devolve uma lista com todos os docentes da Instituição com um determinado estado.  
**Flag:** 0 (Função de consulta)  
**Modo de execução:** 0  
**Retorna bytes:** Não  

#### 📥 Parâmetros de Entrada
- `TpUtil(int)`
- `CdUtil(int)`
- `PwdUtil(pwd)`
- `Estado(string/Opcional)`

#### 📤 Parâmetros de Saída
- `NDocente`
- `Login`
- `Email`
- `NomeCompleto`
- `Estado`
- `CdFaculd`
- `DgFaculd`
- `CdPolo`
- `DgPolo`
- `NContabilistico`

---

### GetCursos
**Status:** ✅ Disponível  
**Código:** 3  
**Descrição:** Obter lista dos cursos.  
**Flag:** 0 (Função de consulta)  
**Modo de execução:** 0  
**Retorna bytes:** Não  

#### 📥 Parâmetros de Entrada
- `CdUniOrg(int/Opcional)`
- `CdCurso(int/Opcional)`
- `CdTpCurso(int/Opcional)`
- `Estado(string/Opcional)`
- `CdPolo(int/Opcional)`
- `CdFaculd(int/Opcional)`
- `CursoPermVer(string/Opcional)`
- `CdUtil(int/Opcional)`
- `AbertoCandOnlineSophia(string/Opcional)`
- `CdLingua(string/Opcional)`
- `DtAudithUpdatedIni(string/Opcional)`
- `DtAudithUpdatedEnd(string/Opcional)`
- `AudithOption(int/Opcional)`

#### 📤 Parâmetros de Saída
- `CdCurso`
- `NmCurso`
- `AbrCurso`
- `CdTpCurso`
- `TpCurso`
- `NAnos`
- `CdPlanoDef`
- `Estado`
- `SaidasProfiss`
- `RequisitosAcesso`
- `CursoTpPosGrad`
- `CdPolo`
- `DgPolo`
- `CdFaculd`
- `DgFaculd`
- `NmCursoIng`
- `CdTpCursoIntermedio`
- `DgTpCursoIntermedio`
- `CdOferta`
- `DgOferta`
- `AudithCreated`
- `AudithUpdated`
- `EctsDiploma`
- `CodigoCRM`
- `NmComercial`
- `CdLinguaMinistrado`

---

### GetAnosLect
**Status:** ✅ Disponível  
**Código:** 13  
**Descrição:** Devolve anos letivos.  
**Flag:** 0 (Função de consulta)  
**Modo de execução:** 0  
**Retorna bytes:** Não  

#### 📥 Parâmetros de Entrada
- `Origem(int/Opcional)`
- `Formato(int/Opcional)`

#### 📤 Parâmetros de Saída
- `CdAnoLect`
- `AnoLect`

---

### GetPeriodos
**Status:** ✅ Disponível  
**Código:** 14  
**Descrição:** Devolve períodos existentes.  
**Flag:** 0 (Função de consulta)  
**Modo de execução:** 0  
**Retorna bytes:** Não  

#### 📥 Parâmetros de Entrada
- `CdPeriodo(int/Opcional)`
- `CdLingua(string/Opcional)`

#### 📤 Parâmetros de Saída
- `CdPeriodo`
- `DgPeriodo`

---

### GetCursos
**Status:** ✅ Disponível  
**Código:** 3  
**Descrição:** Obter lista dos cursos.  
**Flag:** 0 (Função de consulta)  
**Modo de execução:** 0  
**Retorna bytes:** Não  

#### 📥 Parâmetros de Entrada
- `CdUniOrg(int/Opcional)`
- `CdCurso(int/Opcional)`
- `CdTpCurso(int/Opcional)`
- `Estado(string/Opcional)`
- `CdPolo(int/Opcional)`
- `CdFaculd(int/Opcional)`
- `CursoPermVer(string/Opcional)`
- `CdUtil(int/Opcional)`
- `AbertoCandOnlineSophia(string/Opcional)`
- `CdLingua(string/Opcional)`
- `DtAudithUpdatedIni(string/Opcional)`
- `DtAudithUpdatedEnd(string/Opcional)`
- `AudithOption(int/Opcional)`

#### 📤 Parâmetros de Saída
- `CdCurso`
- `NmCurso`
- `AbrCurso`
- `CdTpCurso`
- `TpCurso`
- `NAnos`
- `CdPlanoDef`
- `Estado`
- `SaidasProfiss`
- `RequisitosAcesso`
- `CursoTpPosGrad`
- `CdPolo`
- `DgPolo`
- `CdFaculd`
- `DgFaculd`
- `NmCursoIng`
- `CdTpCursoIntermedio`
- `DgTpCursoIntermedio`
- `CdOferta`
- `DgOferta`
- `AudithCreated`
- `AudithUpdated`
- `EctsDiploma`
- `CodigoCRM`
- `NmComercial`
- `CdLinguaMinistrado`

---

### GetPEstudos
**Status:** ✅ Disponível  
**Código:** 4  
**Descrição:** Obter planos de estudos.  
**Flag:** 0 (Função de consulta)  
**Modo de execução:** 0  
**Retorna bytes:** Não  

#### 📥 Parâmetros de Entrada
- `CdCurso(int)`
- `CdPEstudo(int/Opcional)`
- `Estado(string/Opcional)`
- `CdLingua(string/Opcional)`
- `DtAudithUpdatedIni(string/Opcional)`
- `DtAudithUpdatedEnd(string/Opcional)`

#### 📤 Parâmetros de Saída
- `CdPlano`
- `NmPlano`
- `Estado`
- `AudithCreated`
- `AudithUpdated`

---

### GetTurmas
**Status:** ✅ Disponível  
**Código:** 366  
**Descrição:** Devolve as turmas.  
**Flag:** 0 (Função de consulta)  
**Modo de execução:** 0  
**Retorna bytes:** Não  

#### 📥 Parâmetros de Entrada
- `CdCurso(int/Opcional)`
- `CdPlanoEstudos(int/Opcional)`
- `CdAnoLect(int/Opcional)`
- `CdDepartamento(int/Opcional)`
- `CdCadeira(int/Opcional)`
- `CdRegFreq(int/Opcional)`
- `CdAnoCurricular(int/Opcional)`
- `CdPeriodo(int/Opcional)`

#### 📤 Parâmetros de Saída
- `CdTurma`
- `DgTurma`
- `NumVagas`

---

### GetDisc
**Status:** ✅ Disponível  
**Código:** 206  
**Descrição:** Obter lista das unidades curriculares ativas para um dado período.  
**Flag:** 0 (Função de consulta)  
**Modo de execução:** 0  
**Retorna bytes:** Não  

#### 📥 Parâmetros de Entrada
- `CdPeriodo(int)`
- `CdPolo(int/Opcional)`
- `CdFaculd(int/Opcional)`
- `CdCurso(int/Opcional)`
- `CdPlanoEstudo(int/Opcional)`
- `Estado(string/Opcional)`

#### 📤 Parâmetros de Saída
- `CdDisc`
- `DgCadeira`
- `AbrCadeira`
- `CdCurso`
- `DgCurso`
- `CdPEstudo`
- `DgPEstudo`
- `CdDivisao`
- `DgDivisao`
- `CdPeriodo`
- `DgPeriodo`
- `Estado`
- `TpDisc`
- `CdGrupOpc`
- `DgGrupOpc`
- `NHorasTeo`
- `NHorasPraticas`
- `NHorasTeoPraticas`
- `NHorasSemEstagio`
- `NHorasPraticaLab`
- `NHorasLaboratorio`
- `NHorasTrabCampo`
- `NHorasOrientTutorial`
- `NHorasOutra`

---

### GetDiscHorario
**Status:** ✅ Disponível  
**Código:** 41  
**Descrição:** Obter o horário da unidade curricular.  
**Flag:** 0 (Função de consulta)  
**Modo de execução:** 0  
**Retorna bytes:** Não  

#### 📥 Parâmetros de Entrada
- `CdDis(string/Opcional)`
- `AnoLectivo(int)`
- `CdPeriodo(int)`
- `CdTurma(int/Opcional)`
- `CdRegime(int/Opcional)`
- `CdDocente(int/Opcional)`
- `CdSala(int/Opcional)`
- `CdAulaFrequencia(int/Opcional)`
- `CdLingua(string/Opcional)`

#### 📤 Parâmetros de Saída
- `CdTurma`
- `DgTurma`
- `DiaSemana`
- `HoraIni`
- `MinutoIni`
- `HoraFim`
- `MinutoFim`
- `CdRegime`
- `DgRegime`
- `NmDocente`
- `Sala`
- `CdDocente`
- `CdDis`
- `NmDis`
- `CdSala`
- `CdPEstudo`
- `AbrDis`
- `CdCampus`
- `CdEdificio`
- `CdPiso`
- `CdAulaFrequencia`
- `DtProxima`
- `CorHorarioWin32`
- `IconRegime`

---

### EditLinhaHorario
**Status:** ✅ Disponível  
**Código:** 181  
**Descrição:** Altera dados de um determinado horário (ex: dia da Semana, horário de início ou fim, sala, docente).  
**Flag:** 1 (Função de alteração)  
**Modo de execução:** 0  
**Retorna bytes:** Não  

#### 📥 Parâmetros de Entrada
- `TpUtil(int)`
- `CdUtil(int)`
- `PwdUtil(pwd)`
- `CdCurso(int)`
- `CdDisciplina(string)`
- `NHorario(int)`
- `AnoLectivo(int)`
- `CdPeriodo(int)`
- `AntigoDiaSemana(int)`
- `AntigoHoraIni(int)`
- `AntigoMinuIni(int)`
- `NovoDiaSemana(int)`
- `NovoCdRegime(int)`
- `NovoHoraIni(int)`
- `NovoMinuIni(int)`
- `NovoHoraFim(int)`
- `NovoMinuFim(int)`
- `NovoCdSala(int/Opcional)`
- `NovoCdDocente(int/Opcional)`
- `CdTpInscricao(int/Opcional)`
- `CdAulaFrequencia(int/Opcional)`

#### 📤 Parâmetros de Saída
- `Retorno`

---

### PutHorario
**Status:** ✅ Disponível  
**Código:** 211  
**Descrição:** Insere uma linha de horário para uma determinada turma.  
**Flag:** 1 (Função de alteração)  
**Modo de execução:** 0  
**Retorna bytes:** Não  

#### 📥 Parâmetros de Entrada
- `TpUtil(int)`
- `CdUtil(int)`
- `PwdUtil(string)`
- `CdDis(string)`
- `NHorario(int)`
- `DiaSemana(int)`
- `HoraIni(int)`
- `MinuIni(int)`
- `HoraFim(int)`
- `MinuFim(int)`
- `CdRegime(int)`
- `CdCurso(int)`
- `AnoLect(int)`
- `CdPeriodo(int)`
- `CdSala(int/Opcional)`
- `CdDocente(int/Opcional)`
- `CdTpInscricao(int/Opcional)`
- `CdAulaFrequencia(int/Opcional)`

#### 📤 Parâmetros de Saída
- `Retorno`

---

## 💡 Recomendações de Implementação

### ✅ Endpoints Prontos para Implementação
- **`GetDocentes`** (Requer parâmetros): Devolve uma lista com todos os docentes da Instituição com um determinado estado.
- **`GetCursos`** (Requer parâmetros): Obter lista dos cursos.
- **`GetAnosLect`** (Requer parâmetros): Devolve anos letivos.
- **`GetPeriodos`** (Requer parâmetros): Devolve períodos existentes.
- **`GetCursos`** (Requer parâmetros): Obter lista dos cursos.
- **`GetPEstudos`** (Requer parâmetros): Obter planos de estudos.
- **`GetTurmas`** (Requer parâmetros): Devolve as turmas.
- **`GetDisc`** (Requer parâmetros): Obter lista das unidades curriculares ativas para um dado período.
- **`GetDiscHorario`** (Requer parâmetros): Obter o horário da unidade curricular.
- **`EditLinhaHorario`** (Requer parâmetros): Altera dados de um determinado horário (ex: dia da Semana, horário de início ou fim, sala, docente).
- **`PutHorario`** (Requer parâmetros): Insere uma linha de horário para uma determinada turma.

### 🔧 Próximos Passos
1. **Implementar endpoints simples** (sem parâmetros de entrada)
2. **Testar chamadas Execute** com parâmetros de saída descobertos
3. **Investigar parâmetros de entrada** para funções mais complexas
4. **Configurar autenticação** se necessário para funções de edição

---
**Relatório gerado em:** 2025-07-31 14:27:39📊 RESUMO FINAL:
   ✅ Endpoints encontrados: 11/11
   ❌ Endpoints com erro: 0
📄 Relatório salvo em: LOGS\endpoint_analysis_8_selected_2025-07-31_14-27-31.md
