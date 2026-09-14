# Roteiro do vídeo executivo

Público: gestores públicos e lideranças educacionais. Versão com narração sintética disponível em `media/video_executivo.mp4`. O grupo deve revisar o conteúdo e decidir sobre sua apresentação final. A narração não imita a voz de nenhum integrante.

## 1 O problema educacional

Como transformar dados de alfabetização em apoio à decisão pública? Nosso projeto usa informações históricas e contexto dos municípios para estimar o risco de um aluno avaliado não estar alfabetizado. A proposta é organizar a investigação e o apoio pedagógico. O modelo não substitui a avaliação de professores e gestores, nem consegue distinguir crianças que compartilham os mesmos atributos. Ele oferece uma leitura do contexto educacional.

## 2 A base construída

Partimos da arquitetura medalhão da Fase dois e dos microdados da Avaliação da Alfabetização. A fonte reúne três milhões e oitocentos mil registros de dois mil e vinte e três e dois mil e vinte e quatro. Selecionamos cerca de um milhão e oitocentos e cinquenta mil alunos presentes, com resultado válido em dois mil e vinte e quatro. Acrescentamos indicadores municipais anteriores, população e contexto econômico. O processamento individual fica no BigQuery; identificadores de aluno e escola não são publicados na Gold.

## 3 Como o modelo foi validado

O treinamento representa todos os alunos elegíveis por meio de perfis e contagens. Mantivemos municípios inteiros em conjuntos diferentes de treino, validação e teste. Comparamos uma referência simples, regressão logística e um modelo de árvores. O pré-processamento foi ajustado apenas no treino. Não usamos a proficiência individual da própria avaliação, pois ela revelaria a resposta. A regressão logística foi selecionada na validação. O teste contempla municípios que não participaram do ajuste.

## 4 O que os resultados mostram

Com o limiar padrão, o modelo acertou cerca de sessenta e cinco por cento dos casos, contra sessenta e dois por cento da referência simples. A capacidade de distinguir os grupos ainda é limitada. Ao reduzir o limiar de risco, identificamos aproximadamente setenta por cento dos alunos não alfabetizados, mas sinalizamos mais da metade da população avaliada. Isso exige discutir a capacidade de atendimento e o custo dos alertas falsos. Não basta olhar uma única métrica.

## 5 Os principais insights

A média municipal anterior de português e a unidade da federação tiveram maior importância preditiva. Esses resultados são associações; não comprovam causas da alfabetização. Também encontramos grandes diferenças de identificação do risco entre estados. Os grupos de municípios com perfis econômicos semelhantes ajudam a organizar comparações mais contextualizadas. Um ranking territorial pode orientar onde investigar primeiro, sempre acompanhado do tamanho da população avaliada e do conhecimento das equipes locais.

## 6 Aplicação para políticas públicas

O uso proposto é apoiar visitas técnicas, formação docente e investigação de barreiras locais. Para as metas de dois mil e vinte e cinco, construímos cenários condicionais: manutenção do resultado anterior ou crescimento de cinco e dez pontos percentuais. Esses cenários mostram o esforço necessário; não são previsões validadas. A priorização deve combinar risco, número de alunos, recursos disponíveis e diagnóstico pedagógico. Os efeitos das ações precisam ser acompanhados ao longo do tempo.

## 7 Limitações e evolução

Esta é uma análise exploratória e retrospectiva. Ainda não temos validação em um novo ano, e faltam características individuais anteriores à avaliação. Os dados representam alunos presentes com resultado válido, não todas as crianças brasileiras. A próxima evolução deve incluir novas coortes, informações de trajetória escolar com vínculo seguro, avaliação externa e monitoramento regional dos erros. Entregamos uma base reproduzível para aprender com os dados e orientar decisões com transparência.
